#ifndef IM2_G67_COLLISION_H
#define IM2_G67_COLLISION_H
/* CPU-only source-triangle blocking. Z-up, source units.
 * No synthesized walls. Native Vita and host regressions share this code. */
#include <math.h>
#include <stdint.h>
typedef struct { float x,y,z; } G67Vec;
typedef struct {
    G67Vec p[3];
    float minx,maxx,miny,maxy,minz,maxz;
    G67Vec normal;
    int wall;
} G67Tri;
static inline float g67_min(float a,float b){return a<b?a:b;}
static inline float g67_max(float a,float b){return a>b?a:b;}
static inline float g67_clamp(float t,float a,float b){return g67_min(g67_max(t,a),b);}
static inline float g67_dist2(float x,float y,float ax,float ay,float bx,float by){
    float dx=bx-ax,dy=by-ay,l2=dx*dx+dy*dy;
    float t=l2>1.e-10f?g67_clamp(((x-ax)*dx+(y-ay)*dy)/l2,0.f,1.f):0.f;
    dx=x-(ax+t*dx);dy=y-(ay+t*dy);
    return dx*dx+dy*dy;
}
/* Source triangle slice. Vertices on the plane are retained.
 * Choose the longest intersection segment when 3 points are available. */
static inline int g67_slice(const G67Tri *a,float z,float *ax,float *ay,float *bx,float *by){
    float hx[6],hy[6];int n=0;
    for(int k=0;k<3;k++){
        G67Vec p=a->p[k],q=a->p[(k+1)%3];
        float dz=q.z-p.z;
        if(fabsf(p.z-z)<=1.e-5f){
            int duplicate=0;
            for(int t=0;t<n;t++)if(g67_dist2(p.x,p.y,hx[t],hy[t],hx[t],hy[t])<1.e-8f)duplicate=1;
            if(!duplicate){hx[n]=p.x;hy[n]=p.y;n++;}
        }
        if((p.z<z&&q.z>z)||(p.z>z&&q.z<z)){
            float alpha=(z-p.z)/dz;
            float x=p.x+alpha*(q.x-p.x),y=p.y+alpha*(q.y-p.y);
            int duplicate=0;
            for(int t=0;t<n;t++)if(g67_dist2(x,y,hx[t],hy[t],hx[t],hy[t])<1.e-8f)duplicate=1;
            if(!duplicate){hx[n]=x;hy[n]=y;n++;}
        }
    }
    if(n<2)return 0;
    float best=-1.f;
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){
        float d=g67_dist2(hx[i],hy[i],hx[j],hy[j],hx[j],hy[j]);
        if(d>best){best=d;*ax=hx[i];*ay=hy[i];*bx=hx[j];*by=hy[j];}
    }
    return best>1.e-10f;
}
/* Dynamic face/actor overlap sampling catches original ankle and head-level
 * walls skipped by the old three fixed torso sample heights. */
static inline int g67_wall_clear_at(const G67Tri *faces,uint32_t count,
                                    float x,float y,float feet,float radius,float height){
    if(!faces||!isfinite(x)||!isfinite(y)||!isfinite(feet)||
       !isfinite(radius)||!isfinite(height)||radius<=0.f||height<=0.f)return 0;
    if(x < -325.f+radius || x > 331.f-radius ||
       y < -352.f+radius || y > 255.f-radius)return 0;
    for(uint32_t i=0;i<count;i++){
        const G67Tri *t=&faces[i];
        if(!t->wall||t->maxz<feet||t->minz>feet+height||
           x<t->minx-radius||x>t->maxx+radius||
           y<t->miny-radius||y>t->maxy+radius)continue;
        float low=g67_max(t->minz,feet+.005f);
        float high=g67_min(t->maxz,feet+height-.005f);
        if(high<low)continue;
        float planes[3]={low,(low+high)*.5f,high};
        for(int k=0;k<3;k++){
            float ax=0,ay=0,bx=0,by=0;
            if(g67_slice(t,planes[k],&ax,&ay,&bx,&by) &&
               g67_dist2(x,y,ax,ay,bx,by)<radius*radius)return 0;
        }
    }
    return 1;
}
/* Flight need not have a walkable source floor below; ground mode does. */
static inline int g67_horizontal_ok(int flying,int wall_clear,int floor_found,
                                    float oldfeet,float nextfloor){
    if(!wall_clear)return 0;
    if(flying)return 1;
    return floor_found&&isfinite(nextfloor)&&
           nextfloor>=oldfeet-.35f&&nextfloor<=oldfeet+.45f;
}
#endif
