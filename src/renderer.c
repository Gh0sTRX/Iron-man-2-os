#include "b24/b24_unified/b24_c1l1_map.h"
#include "renderer.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX(a,b) ((a)>(b)?(a):(b))
#define CLAMP(v,a,b) (MAX((a),MIN((v),(b))))

static unsigned im2_get_u32(FILE *f, int *ok) {
    unsigned char p[4];
    if(fread(p,1,4,f)!=4){*ok=0;return 0;}
    return (unsigned)p[0]|((unsigned)p[1]<<8)|((unsigned)p[2]<<16)|((unsigned)p[3]<<24);
}
static unsigned short im2_get_u16(FILE *f, int *ok) {
    unsigned char p[2];
    if(fread(p,1,2,f)!=2){*ok=0;return 0;}
    return (unsigned short)(p[0]|(p[1]<<8));
}
static float im2_get_f32(FILE *f, int *ok){
    uint32_t v=im2_get_u32(f,ok);float o=0.0f;
    memcpy(&o,&v,4);return o;
}
void im2_free(IM2Model *m){
    if(!m)return;
    free(m->vertices);free(m->triangles);free(m->texture);
    memset(m,0,sizeof(*m));
}
int im2_load(IM2Model *dst,const char *path){
    FILE *f=fopen(path,"rb");
    if(!f)return 0;
    IM2Model tmp={0};int ok=1;char magic[4];
    if(fread(magic,1,4,f)!=4||memcmp(magic,"IM2T",4)!=0){fclose(f);return 0;}
    tmp.nv=im2_get_u32(f,&ok);tmp.nt=im2_get_u32(f,&ok);
    tmp.tw=im2_get_u32(f,&ok);tmp.th=im2_get_u32(f,&ok);
    if(!ok||!tmp.nv||tmp.nv>IM2_MAXV||!tmp.nt||tmp.nt>IM2_MAXT||
       !tmp.tw||!tmp.th||tmp.tw>2048||tmp.th>2048){fclose(f);return 0;}
    tmp.vertices=(IM2Vertex*)malloc(sizeof(IM2Vertex)*tmp.nv);
    tmp.triangles=(IM2Triangle*)malloc(sizeof(IM2Triangle)*tmp.nt);
    tmp.texture=(unsigned char*)malloc((size_t)tmp.tw*tmp.th*4);
    if(!tmp.vertices||!tmp.triangles||!tmp.texture){fclose(f);im2_free(&tmp);return 0;}
    for(uint32_t i=0;i<tmp.nv;i++){
        IM2Vertex *v=&tmp.vertices[i];
        v->x=im2_get_f32(f,&ok);v->y=im2_get_f32(f,&ok);v->z=im2_get_f32(f,&ok);
        v->u=im2_get_f32(f,&ok);v->v=im2_get_f32(f,&ok);
        if(!isfinite(v->x)||!isfinite(v->y)||!isfinite(v->z)||!isfinite(v->u)||!isfinite(v->v))ok=0;
    }
    for(uint32_t i=0;i<tmp.nt;i++){
        IM2Triangle *t=&tmp.triangles[i];
        t->i0=im2_get_u16(f,&ok);t->i1=im2_get_u16(f,&ok);t->i2=im2_get_u16(f,&ok);
        if(t->i0>=tmp.nv||t->i1>=tmp.nv||t->i2>=tmp.nv)ok=0;
    }
    if(fread(tmp.texture,4,(size_t)tmp.tw*tmp.th,f)!=(size_t)tmp.tw*tmp.th)ok=0;
    fclose(f);
    if(!ok){im2_free(&tmp);return 0;}
    float minz=tmp.vertices[0].z,maxz=minz;
    for(uint32_t i=1;i<tmp.nv;i++){
        minz=MIN(minz,tmp.vertices[i].z);maxz=MAX(maxz,tmp.vertices[i].z);
    }
         tmp.center_z=(minz+maxz)*0.5f;
     tmp.native_bind_min_z=minz; /* actual 2010 original rest mesh, not animated foot bob */
    im2_free(dst);*dst=tmp;
    return 1;
}

typedef struct {float sx,sy,iz,uiz,viz,cx,cy,cz;} Projected;
static Projected transformed[IM2_MAXV];
static uint32_t packrgb(unsigned r,unsigned g,unsigned b){
    return 0xff000000u | ((r&255)<<16)|((g&255)<<8)|(b&255);
}
static void pixel(uint32_t *out,int x,int y,uint32_t color){
    if(x>=0&&x<IM2_W&&y>=0&&y<IM2_H)out[y*IM2_W+x]=color;
}
static void line(uint32_t *out,int x0,int y0,int x1,int y1,uint32_t color){
    int dx=abs(x1-x0),dy=abs(y1-y0);
    int sx=x0<x1?1:-1,sy=y0<y1?1:-1;
    int err=dx-dy;
    for(int i=0;i<2500;i++){
        pixel(out,x0,y0,color);
        if(x0==x1&&y0==y1)break;
        int e=err*2;
        if(e>-dy){err-=dy;x0+=sx;}
        if(e<dx){err+=dx;y0+=sy;}
    }
}

/* Built-in 5x7 uppercase font. No SDL_ttf dependency. */
static const unsigned char glyphs[][7]={
    {14,17,17,31,17,17,17},/* A */{30,17,17,30,17,17,30},
    {15,16,16,16,16,16,15},{30,17,17,17,17,17,30},
    {31,16,16,30,16,16,31},{31,16,16,30,16,16,16},
    {15,16,16,19,17,17,15},{17,17,17,31,17,17,17},
    {31,4,4,4,4,4,31},{7,2,2,2,18,18,12},
    {17,18,20,24,20,18,17},{16,16,16,16,16,16,31},
    {17,27,21,21,17,17,17},{17,25,21,19,17,17,17},
    {14,17,17,17,17,17,14},{30,17,17,30,16,16,16},
    {14,17,17,17,21,18,13},{30,17,17,30,20,18,17},
    {15,16,16,14,1,1,30},{31,4,4,4,4,4,4},
    {17,17,17,17,17,17,14},{17,17,17,17,17,10,4},
    {17,17,17,21,21,21,10},{17,17,10,4,10,17,17},
    {17,17,10,4,4,4,4},{31,1,2,4,8,16,31}
};
static const unsigned char numerals[][7]={
    {14,17,19,21,25,17,14},{4,12,4,4,4,4,14},
    {14,17,1,2,4,8,31},{30,1,1,14,1,1,30},
    {2,6,10,18,31,2,2},{31,16,16,30,1,1,30},
    {15,16,16,30,17,17,14},{31,1,2,4,8,8,8},
    {14,17,17,14,17,17,14},{14,17,17,15,1,1,30}
};
static void write_text(uint32_t *out,int x,int y,const char *s,uint32_t color,int scale){
    while(*s){
        unsigned char ch=(unsigned char)*s++;
        const unsigned char *g=0;unsigned char special[7]={0};
        if(ch>='A'&&ch<='Z')g=glyphs[ch-'A'];
        if(ch>='0'&&ch<='9')g=numerals[ch-'0'];
        if(ch==':'){special[1]=4;special[4]=4;g=special;}
        if(ch=='-'){special[3]=14;g=special;}
        if(ch=='/'){special[0]=1;special[1]=2;special[2]=4;special[3]=8;special[4]=16;g=special;}
        if(ch=='.'){special[6]=4;g=special;}
        if(g){
            for(int row=0;row<7;row++)for(int col=0;col<5;col++)if(g[row]&(1<<(4-col)))
                for(int dy=0;dy<scale;dy++)for(int dx=0;dx<scale;dx++)
                    pixel(out,x+col*scale+dx,y+row*scale+dy,color);
        }
        x+=6*scale;
    }
}
static void draw_background(uint32_t *out,float yaw){
    for(int y=0;y<IM2_H;y++){
        float t=(float)y/IM2_H;
        unsigned r=(unsigned)(6+8*t),g=(unsigned)(11+16*t),b=(unsigned)(23+23*t);
        uint32_t c=packrgb(r,g,b);
        for(int x=0;x<IM2_W;x++)out[y*IM2_W+x]=c;
    }
    /* Grid gives the prototype a real viewer layout. */
    int floor_y=232;
    for(int i=0;i<12;i++){
        int x=(i*52+(int)(yaw*8))%600-60;
        line(out,240,floor_y-5,x,IM2_H-22,packrgb(20,40,54));
    }
    for(int i=0;i<4;i++){
        int y=floor_y+i*i*3;
        line(out,0,y,IM2_W-1,y,packrgb(20,40,54));
    }
}
static void render_triangle(uint32_t *pixels,float *depth,const IM2Model *m,
                            const Projected *a,const Projected *b,const Projected *c){
    /* Identical perspective-correct UV/depth to B4; incremental barycentric
       edges avoid recomputing four products for EVERY candidate pixel. */
    if(a->iz<=0||b->iz<=0||c->iz<=0)return;
    const float ax=a->sx,ay=a->sy,bx=b->sx,by=b->sy,cx=c->sx,cy=c->sy;
    const float den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy);
    if(fabsf(den)<0.0001f)return;
    const int x0=CLAMP((int)floorf(MIN(ax,MIN(bx,cx))),0,IM2_W-1);
    const int x1=CLAMP((int)ceilf (MAX(ax,MAX(bx,cx))),0,IM2_W-1);
    const int y0=CLAMP((int)floorf(MIN(ay,MIN(by,cy))),0,IM2_H-1);
    const int y1=CLAMP((int)ceilf (MAX(ay,MAX(by,cy))),0,IM2_H-1);
    if(x1<x0||y1<y0)return;
    const float e1x=b->cx-a->cx,e1y=b->cy-a->cy,e1z=b->cz-a->cz;
    const float e2x=c->cx-a->cx,e2y=c->cy-a->cy,e2z=c->cz-a->cz;
    const float nx=e1y*e2z-e1z*e2y,ny=e1z*e2x-e1x*e2z,nz=e1x*e2y-e1y*e2x;
    const float invnorm=1.0f/sqrtf(nx*nx+ny*ny+nz*nz+1e-20f);
    const float intensity=MIN(1.0f,0.45f+0.55f*fabsf((nx*.35f-ny*.65f+nz*.68f)*invnorm));
    const float invden=1.0f/den;
    const float dpdx=(by-cy)*invden,dqdx=(cy-ay)*invden;
    const float dpdy=(cx-bx)*invden,dqdy=(ax-cx)*invden;
    const float x0f=x0+0.5f-cx,y0f=y0+0.5f-cy;
    float pr=(by-cy)*x0f*invden+(cx-bx)*y0f*invden;
    float qr=(cy-ay)*x0f*invden+(ax-cx)*y0f*invden;
    const float dizdp=a->iz-c->iz, dizdq=b->iz-c->iz;
    const float duzdp=a->uiz-c->uiz,duzdq=b->uiz-c->uiz;
    const float dvzdp=a->viz-c->viz,dvzdq=b->viz-c->viz;
    const float dizdx=dpdx*dizdp+dqdx*dizdq;
    const float duzdx=dpdx*duzdp+dqdx*duzdq;
    const float dvzdx=dpdx*dvzdp+dqdx*dvzdq;
    float izr=c->iz+pr*dizdp+qr*dizdq;
    float uzr=c->uiz+pr*duzdp+qr*duzdq;
    float vzr=c->viz+pr*dvzdp+qr*dvzdq;
    const float dizdy=dpdy*dizdp+dqdy*dizdq;
    const float duzdy=dpdy*duzdp+dqdy*duzdq;
    const float dvzdy=dpdy*dvzdp+dqdy*dvzdq;
    const uint32_t tw=m->tw,th=m->th;
    for(int y=y0;y<=y1;y++){
        float p=pr,q=qr,iz=izr,uz=uzr,vz=vzr;
        uint32_t *outrow=pixels+(size_t)y*IM2_W;
        float *zrow=depth+(size_t)y*IM2_W;
        for(int x=x0;x<=x1;x++){
            if(p>=-0.00001f&&q>=-0.00001f&&p+q<=1.00001f&&iz>zrow[x]){
                /* All four verified IM2T atlases have UVs in (0,1).
                   Perspective interpolation stays within that convex range,
                   allowing us to omit expensive floorf-based texture wrap. */
                float inviz=1.0f/iz;
                unsigned tx=(unsigned)CLAMP((int)(uz*inviz*tw),0,(int)tw-1);
                unsigned ty=(unsigned)CLAMP((int)(vz*inviz*th),0,(int)th-1);
                const unsigned char *c4=m->texture+((size_t)ty*tw+tx)*4;
                if(c4[3]>=15){
                    zrow[x]=iz;
                    outrow[x]=packrgb((unsigned)(c4[0]*intensity),
                                      (unsigned)(c4[1]*intensity),
                                      (unsigned)(c4[2]*intensity));
                }
            }
            p+=dpdx;q+=dqdx;iz+=dizdx;uz+=duzdx;vz+=dvzdx;
        }
        pr+=dpdy;qr+=dqdy;izr+=dizdy;uzr+=duzdy;vzr+=dvzdy;
    }
}

static int world_to_screen(const IM2Camera *c,float wx,float wy,float wz,float *sx,float *sy,float *invdepth){
    float rx=cosf(c->orbit),ry=-sinf(c->orbit),fx=sinf(c->orbit),fy=cosf(c->orbit);
    float r=c->camera_distance*cosf(c->pitch);
    float camx=c->cam_x-fx*r+rx*.55f;
    float camy=c->cam_y-fy*r+ry*.55f;
    float camz=c->cam_z+c->camera_distance*sinf(c->pitch)+.07f;
    float dx=wx-camx,dy=wy-camy,dz=wz-camz;
    float lr=dx*rx+dy*ry,depth=dx*fx+dy*fy;
    float dzview=depth*sinf(c->pitch)+dz*cosf(c->pitch);
    float d=depth*cosf(c->pitch)-dz*sinf(c->pitch);
    if(d<=.15f)return 0;
    if(sx)*sx=240.f+350.f*lr/d;
    if(sy)*sy=100.f-350.f*dzview/d;
    if(invdepth)*invdepth=1.f/d;
    return 1;
}

/* B17: bounded checkerboard rectangles on WORLD z=-1 plane. Every vertex
   goes through existing third-person camera projection. This is not a
   fixed-position 2-D HUD background and uses depth with the armor mesh. */
typedef struct {float x,y,iz;int ok;} B17Projected;
static B17Projected b17_project(const IM2Camera *cam,float x,float y,float z){
    B17Projected p={0};
    p.ok=world_to_screen(cam,x,y,z,&p.x,&p.y,&p.iz);
    if(!isfinite(p.x)||!isfinite(p.y)||fabsf(p.x)>3500||fabsf(p.y)>3500)p.ok=0;
    return p;
}
static void b17_floor_tri(uint32_t *out,float *depth,B17Projected a,
                          B17Projected b,B17Projected c,uint32_t col){
    if(!a.ok||!b.ok||!c.ok)return;
    float det=(b.y-c.y)*(a.x-c.x)+(c.x-b.x)*(a.y-c.y);
    if(fabsf(det)<.001f)return;
    int loX=CLAMP((int)floorf(MIN(a.x,MIN(b.x,c.x))),0,IM2_W-1);
    int hiX=CLAMP((int)ceilf(MAX(a.x,MAX(b.x,c.x))),0,IM2_W-1);
    int loY=CLAMP((int)floorf(MIN(a.y,MIN(b.y,c.y))),0,IM2_H-1);
    int hiY=CLAMP((int)ceilf(MAX(a.y,MAX(b.y,c.y))),0,IM2_H-1);
    /* Clip to gameplay space so top HUD is never hidden by the ground plane. */
    loY=MAX(loY,25);hiY=MIN(hiY,IM2_H-18);
    if(loX>hiX||loY>hiY)return;
    float inv=1.0f/det;
    for(int y=loY;y<=hiY;y++){
        for(int x=loX;x<=hiX;x++){
            float wx=x+.5f,wy=y+.5f;
            float q=((b.y-c.y)*(wx-c.x)+(c.x-b.x)*(wy-c.y))*inv;
            float r=((c.y-a.y)*(wx-c.x)+(a.x-c.x)*(wy-c.y))*inv;
            float t=1.f-q-r;
            if(q<-.0001f||r<-.0001f||t<-.0001f)continue;
            float iz=q*a.iz+r*b.iz+t*c.iz;
            size_t p=(size_t)y*IM2_W+(size_t)x;
            if(iz>depth[p]){depth[p]=iz;out[p]=col;}
        }
    }
}

/* B24-C1: source-authentic C1L1 city triangles: exact 2010 BDAE vertices.
   This temporary bounded CPU pass proves integration into B24; next replace
   scene and animated armor draws with one native vitaGL/GXM renderer.
   Only draw local geometry to avoid the B17 480x272 per-pixel FPS collapse. */

/* B24-C2 stopgap: bounded CPU diagnostic triangles, 4x4 spatial sampling.
   The correct long-term rendering path is Vita GPU geometry with depth.
   Cap per-stage work in PIXEL BLOCK TESTS, not only triangle count. */
static void b24_c1_tri_fast(uint32_t *pixels,float *depth,
        B17Projected a,B17Projected b,B17Projected c,
        uint32_t color,int *remaining){
    if(!remaining||*remaining<=0||!a.ok||!b.ok||!c.ok)return;
    float det=(b.y-c.y)*(a.x-c.x)+(c.x-b.x)*(a.y-c.y);
    if(!isfinite(det)||fabsf(det)<0.001f)return;
    int minx=CLAMP((int)floorf(MIN(a.x,MIN(b.x,c.x))),0,IM2_W-1);
    int maxx=CLAMP((int)ceilf(MAX(a.x,MAX(b.x,c.x))),0,IM2_W-1);
    int miny=CLAMP((int)floorf(MIN(a.y,MIN(b.y,c.y))),25,IM2_H-22);
    int maxy=CLAMP((int)ceilf(MAX(a.y,MAX(b.y,c.y))),25,IM2_H-22);
    if(minx>maxx||miny>maxy)return;
    /* Fixed align: continuous tiles where adjacent triangles meet. */
    minx=(minx/4)*4;
    miny=(miny/4)*4;
    const float inv=1.f/det;
    for(int y=miny;y<=maxy && *remaining>0;y+=4){
        for(int x=minx;x<=maxx && *remaining>0;x+=4){
            --*remaining;
            float px=(float)x+2.f,py=(float)y+2.f;
            float q=((b.y-c.y)*(px-c.x)+(c.x-b.x)*(py-c.y))*inv;
            float r=((c.y-a.y)*(px-c.x)+(a.x-c.x)*(py-c.y))*inv;
            float t=1.f-q-r;
            if(q<-.0001f||r<-.0001f||t<-.0001f)continue;
            float z=q*a.iz+r*b.iz+t*c.iz;
            for(int yy=y;yy<y+4 && yy<=maxy && yy<IM2_H;yy++){
                for(int xx=x;xx<x+4 && xx<=maxx && xx<IM2_W;xx++){
                    size_t k=(size_t)yy*IM2_W+(size_t)xx;
                    if(z>depth[k]){depth[k]=z;pixels[k]=color;}
                }
            }
        }
    }
}

static int b24_c1_scene(uint32_t *out,float *depth,const IM2Camera *cam){
    static int loaded=0;
    if(!loaded)loaded=b24_c1l1_load("maps/C1L1_environment.im2map")?1:-1;
    if(loaded!=1)return 0;
    const int limits[4]={65,180,60,60};
    int sample_budget[4]={6200,9000,1800,1400};
    int used[4]={0,0,0,0};
    const float radius=135.f;
    const float minX=cam->player_x-radius,maxX=cam->player_x+radius;
    const float minY=cam->player_y-radius,maxY=cam->player_y+radius;
    const size_t n=b24_c1l1_count();
    for(size_t i=0;i<n;i++){
        const B24C1Triangle *tri=b24_c1l1_triangle(i);
        if(!tri||tri->category>3u)continue;
        int category=(int)tri->category;
        if(used[category]>=limits[category])continue;
        float a=tri->p[0],b=tri->p[3],c=tri->p[6];
        float d=tri->p[1],e=tri->p[4],f=tri->p[7];
        if((a<minX&&b<minX&&c<minX) ||
           (a>maxX&&b>maxX&&c>maxX) ||
           (d<minY&&e<minY&&f<minY) ||
           (d>maxY&&e>maxY&&f>maxY))continue;
        /* B17 project retains original world Z-up and the armor depth sign. */
        B17Projected p0=b17_project(cam,tri->p[0],tri->p[1],tri->p[2]);
        B17Projected p1=b17_project(cam,tri->p[3],tri->p[4],tri->p[5]);
        B17Projected p2=b17_project(cam,tri->p[6],tri->p[7],tri->p[8]);
        if(!p0.ok||!p1.ok||!p2.ok)continue;
        /* Reject triangles trivially outside screen, not merely outside radius. */
        if((p0.x<0&&p1.x<0&&p2.x<0) ||
           (p0.x>=IM2_W&&p1.x>=IM2_W&&p2.x>=IM2_W) ||
           (p0.y<0&&p1.y<0&&p2.y<0) ||
           (p0.y>=IM2_H&&p1.y>=IM2_H&&p2.y>=IM2_H))continue;
        const uint32_t rgb=tri->rgb;
        uint32_t color=packrgb((int)((rgb>>16)&255u),
                               (int)((rgb>>8)&255u),
                               (int)(rgb&255u));
        b24_c1_tri_fast(out,depth,p0,p1,p2,color,&sample_budget[category]);
        used[category]++;
    }
    return 1;
}

static void b17_world_floor(uint32_t *out,float *depth,const IM2Camera *cam){
    const int baseX=(int)floorf(cam->player_x/2.f)*2;
    const int baseY=(int)floorf(cam->player_y/2.f)*2;
    for(int j=-5;j<=5;j++)for(int i=-5;i<=5;i++){
        float x=(float)(baseX+2*i),y=(float)(baseY+2*j);
        B17Projected a=b17_project(cam,x,y,-1.f);
        B17Projected b=b17_project(cam,x+2.f,y,-1.f);
        B17Projected c=b17_project(cam,x+2.f,y+2.f,-1.f);
        B17Projected d=b17_project(cam,x,y+2.f,-1.f);
        /* Muted cyan/steel panels with bright 4x4m positional stripes. */
        int edge=(i%4==0||j%4==0);
        uint32_t color=edge?packrgb(28,83,112):
          ((i+j)&1)?packrgb(20,59,82):packrgb(43,96,117);
        if(i==0 && j==0)color=packrgb(73,117,91);
        b17_floor_tri(out,depth,a,b,c,color);
        b17_floor_tri(out,depth,a,c,d,color);
    }
}

static void world_grid(uint32_t *pixels,const IM2Camera *cam){
    const uint32_t color=packrgb(20,49,60);
    /* Sparse first-person-relative grid: visual world motion while flying. */
    const int x0=(int)floorf(cam->player_x/2.f)*2;
    const int y0=(int)floorf(cam->player_y/2.f)*2;
    for(int k=-10;k<=10;k++){
        float ax,ay,bx,by;
        if(world_to_screen(cam,(float)(x0+k*2),(float)(y0-20),-1.0f,&ax,&ay,NULL) &&
           world_to_screen(cam,(float)(x0+k*2),(float)(y0+20),-1.0f,&bx,&by,NULL))
           if(fabsf(ax)<10000&&fabsf(bx)<10000&&fabsf(ay)<10000&&fabsf(by)<10000&&ay>153&&by>153)
            line(pixels,(int)ax,(int)ay,(int)bx,(int)by,color);
        if(world_to_screen(cam,(float)(x0-20),(float)(y0+k*2),-1.0f,&ax,&ay,NULL) &&
           world_to_screen(cam,(float)(x0+20),(float)(y0+k*2),-1.0f,&bx,&by,NULL))
           if(fabsf(ax)<10000&&fabsf(bx)<10000&&fabsf(ay)<10000&&fabsf(by)<10000&&ay>153&&by>153)
            line(pixels,(int)ax,(int)ay,(int)bx,(int)by,color);
    }
}
static void ring(uint32_t *pixels,int x,int y,int radius,uint32_t color){
    radius=CLAMP(radius,2,40);
    for(int a=0;a<24;a++){
       float t=(float)a*6.28318530718f/24.f,u=(float)(a+1)*6.28318530718f/24.f;
       line(pixels,x+(int)(radius*cosf(t)),y+(int)(radius*sinf(t)),
            x+(int)(radius*cosf(u)),y+(int)(radius*sinf(u)),color);
    }
}
void im2_render(uint32_t *pixels,float *zbuffer,const IM2Model *m,
                const IM2Camera *camera,const char *name,unsigned frame_number){
    (void)frame_number;
    draw_background(pixels,camera->yaw);
    memset(zbuffer,0,sizeof(float)*IM2_W*IM2_H);
    if(camera->third_person){
        int b24_map_ok=b24_c1_scene(pixels,zbuffer,camera);
        /* On-screen diagnostic: distinguishes missing app0: asset from camera culling. */
        write_text(pixels,337,181,b24_map_ok?"C1L1 READY":"C1L1 FAIL",
                   b24_map_ok?packrgb(120,230,168):packrgb(255,108,89),1);
        /* Original C1L1 environment, no B17 grid lines. */
    }
    if(m&&m->nv){
        const float yaw=camera->yaw,pitch=camera->pitch;
        float sy=sinf(yaw),cy=cosf(yaw),sp=sinf(pitch),cp=cosf(pitch);
        float distance=3.70f/camera->zoom+(camera->flying?0.65f:0.0f);
        for(uint32_t i=0;i<m->nv;i++){
            IM2Vertex v=m->vertices[i];
            /* Keep character rotation but translate player in a world-like arena.
             * Keeping translation separate from yaw is important for controls. */
            float x=v.x*cy-v.y*sy+camera->move_x;
            float y=v.x*sy+v.y*cy+camera->move_y;
            float z=v.z-m->center_z+camera->altitude*0.50f+camera->hover_bob;
            float yy=y*cp-z*sp;
            float zz=y*sp+z*cp;
            float dep=distance-yy;
            Projected *p=&transformed[i];
            if(camera->third_person){
                float hx=cosf(camera->player_heading),hy=sinf(camera->player_heading);
                float wx=camera->player_x-v.x*hx-v.y*hy;
                float wy=camera->player_y+v.x*hy-v.y*hx;
                float wz=v.z-m->center_z+camera->player_z+camera->hover_bob;
                float proj_x=0,proj_y=0,inverse=0;
                if(world_to_screen(camera,wx,wy,wz,&proj_x,&proj_y,&inverse)){
                    p->iz=inverse;p->sx=proj_x;p->sy=proj_y;
                    p->cx=wx;p->cy=wy;p->cz=wz;
                }else{p->iz=-1;p->sx=-9999;p->sy=-9999;p->cx=wx;p->cy=wy;p->cz=wz;}
            }else{
                p->cx=x;p->cy=yy;p->cz=zz;
                p->iz=dep>0.15f?1.0f/dep:-1.0f;
                p->sx=IM2_W*0.50f+350.f*x*p->iz;
                p->sy=IM2_H*0.52f-350.f*zz*p->iz;
            }
            p->uiz=v.u*p->iz;p->viz=v.v*p->iz;
        }
        for(uint32_t i=0;i<m->nt;i++){
            IM2Triangle t=m->triangles[i];
            const Projected *a=&transformed[t.i0],*b=&transformed[t.i1],*c=&transformed[t.i2];
            render_triangle(pixels,zbuffer,m,a,b,c);
            if(camera->wireframe && a->iz>0 && b->iz>0 && c->iz>0){
                uint32_t linecol=packrgb(65,208,233);
                line(pixels,(int)a->sx,(int)a->sy,(int)b->sx,(int)b->sy,linecol);
                line(pixels,(int)b->sx,(int)b->sy,(int)c->sx,(int)c->sy,linecol);
                line(pixels,(int)c->sx,(int)c->sy,(int)a->sx,(int)a->sy,linecol);
            }
        }
    }
    if(camera->third_person){
      const uint32_t cyan=packrgb(65,210,235),gold=packrgb(248,204,104);
      if(camera->target_visible)ring(pixels,(int)camera->target_screen_x,
            (int)camera->target_screen_y,(int)camera->target_radius,gold);
      int ax=(int)camera->aim_x,ay=(int)camera->aim_y;
      line(pixels,ax-10,ay,ax-4,ay,cyan);line(pixels,ax+4,ay,ax+10,ay,cyan);
      line(pixels,ax,ay-10,ax,ay-4,cyan);line(pixels,ax,ay+4,ax,ay+10,cyan);
      if(camera->beam_time>0 && camera->weapon_mode!=2 && camera->weapon_mode!=3){
          /* B16: animated ORIGINAL hand vertex (not arbitrary screen center). */
          int palm=camera->b16_active?camera->emitter_vertex:-1;
          int ex=200,ey=153;
          if(palm>=0 && (unsigned)palm<m->nv && transformed[palm].iz>0){
             ex=(int)transformed[palm].sx;ey=(int)transformed[palm].sy;
          }
          const uint32_t beamcol=camera->weapon_mode==1?packrgb(245,255,255):cyan;
          for(int off=-1;off<=1;off++){
             line(pixels,ex,ey+off,ax,ay+off,beamcol);
             if(camera->weapon_mode==1)line(pixels,ex+off,ey,ax+off,ay,gold);
          }
          ring(pixels,ex,ey,camera->weapon_mode==1?7:4,gold);
      }
      if(camera->missile_active){
        float mx=0,my=0,inv=0;
        if(world_to_screen(camera,camera->missile_x,camera->missile_y,camera->missile_z,&mx,&my,&inv)){
          ring(pixels,(int)mx,(int)my,5,gold);ring(pixels,(int)mx,(int)my,2,cyan);
        }
      }
    }
    for(int y=0;y<24;y++)for(int x=0;x<IM2_W;x++)pixels[y*IM2_W+x]=packrgb(9,18,29);
    write_text(pixels,12,8,"IRON MAN 2",packrgb(224,238,243),2);
    write_text(pixels,285,11,camera->b16_active?"B24 C1L1 TEST":(camera->third_person?"VITA MECHANICS B15":"VITA ANIM B13"),packrgb(81,187,210),1);
    line(pixels,0,24,IM2_W-1,24,packrgb(44,96,111));
    write_text(pixels,10,35,name?name:"NO MODEL",packrgb(250,205,109),2);
    write_text(pixels,10,61,camera->wireframe?"WIREFRAME":"ORIGINAL ATLAS",packrgb(111,196,207),1);
    write_text(pixels,10,75,camera->flying?"FLIGHT MODE":"GROUND MODE",packrgb(228,166,90),1);
    char hud[80];
    if(camera->third_person)
        snprintf(hud,sizeof(hud),"X %.1f Y %.1f ALT %.1f",camera->player_x,camera->player_y,camera->player_z);
    else snprintf(hud,sizeof(hud),"X %.1f  Y %.1f  ALT %.1f",camera->move_x,camera->move_y,camera->altitude);
    write_text(pixels,10,89,hud,packrgb(131,195,209),1);
    snprintf(hud,sizeof(hud),"FPS %d",(int)(camera->fps+0.5f));
    write_text(pixels,420,34,hud,packrgb(131,195,209),1);
    snprintf(hud,sizeof(hud),"AN %.0fMS",camera->motion_ms);
    write_text(pixels,412,46,hud,packrgb(131,195,209),1);
    snprintf(hud,sizeof(hud),"CPU %.0fMS",camera->raster_ms);
    write_text(pixels,412,58,hud,packrgb(131,195,209),1);
    snprintf(hud,sizeof(hud),"UP %.0fMS",camera->upload_ms);
    write_text(pixels,412,70,hud,packrgb(131,195,209),1);
    snprintf(hud,sizeof(hud),"COPY %.0fMS",camera->copy_ms);
    write_text(pixels,412,82,hud,packrgb(131,195,209),1);
    snprintf(hud,sizeof(hud),"PRES %.0fMS",camera->present_ms);
    write_text(pixels,412,94,hud,packrgb(131,195,209),1);
    snprintf(hud,sizeof(hud),"VS %s",camera->vsync_active?"ON":(camera->vsync_requested?"FALL":"OFF"));
    write_text(pixels,412,106,hud,camera->profile_error?packrgb(255,117,117):packrgb(250,205,109),1);
    if(camera->third_person){
        snprintf(hud,sizeof(hud),"AIR STAGE %d  CTRL X%s Y%s",camera->flight_stage,camera->invert_x?"INV":"STD",camera->invert_y?"INV":"STD");
        write_text(pixels,10,115,hud,packrgb(110,200,190),1);
        write_text(pixels,10,127,camera->b16_active?"D-UP/DN WEAPON  D-L/R AXIS INV":"D-L X AXIS  D-R LOOK Y  D-UP/DN ZOOM",packrgb(118,154,158),1);
        if(camera->b16_active){
          static const char *weapons[]={"REPULSOR","UNIBEAM","MISSILE","MELEE"};
          snprintf(hud,sizeof(hud),"WEAPON %s  ENERGY %d  COMBO %d",weapons[(camera->weapon_mode+4)%4],(int)(camera->energy+.5f),camera->combo_step);
          write_text(pixels,10,140,hud,packrgb(250,205,109),1);
          if(camera->weapon_mode==3)
              write_text(pixels,10,152,"MELEE COMBO CLIPS FOUND - NOT BAKED",packrgb(255,169,125),1);
        }
        snprintf(hud,sizeof(hud),"WAVE %d HIT %d/3 SHOTS %d",camera->waves+1,camera->hits,camera->shots);
        write_text(pixels,10,102,hud,packrgb(250,205,109),1);
        if(camera->completed)write_text(pixels,270,121,"NEXT WAVE...",packrgb(144,241,155),2);
    }
    for(int y=IM2_H-17;y<IM2_H;y++)for(int x=0;x<IM2_W;x++)pixels[y*IM2_W+x]=packrgb(8,16,28);
    write_text(pixels,7,IM2_H-13,camera->third_person?
      camera->b16_active?"L WALK/RUN R CAM SQ ACT O FLY TRI AIR BOOST": "L MOVE R CAM SQ FIRE O FLY TRI BOOST X SUIT":
      "L MOVE R AIM SQ FIRE O FLY X NEXT SEL VSYNC",packrgb(155,178,188),1);
}
