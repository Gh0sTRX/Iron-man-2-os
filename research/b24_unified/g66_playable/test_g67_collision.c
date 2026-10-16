#include <assert.h>
#include <stdio.h>
#include "g67_collision.h"
static G67Tri panel(float zlow,float zhigh){
    G67Tri t={0};
    t.p[0]=(G67Vec){0.f,-3.f,zlow};
    t.p[1]=(G67Vec){0.f, 3.f,zlow};
    t.p[2]=(G67Vec){0.f, 3.f,zhigh};
    t.minx=t.maxx=0.f;t.miny=-3.f;t.maxy=3.f;
    t.minz=zlow;t.maxz=zhigh;t.wall=1;
    return t;
}
int main(void){
    G67Tri f[3]={panel(.05f,.21f),panel(1.85f,2.08f),panel(0.f,8.f)};
    assert(!g67_wall_clear_at(f,1,.14f,1.f,0.f,.39f,2.15f));
    assert(!g67_wall_clear_at(f+1,1,.15f,1.f,0.f,.39f,2.15f));
    assert(g67_wall_clear_at(f,1,.12f,1.f,2.5f,.39f,2.15f));
    assert(g67_wall_clear_at(f+1,1,.12f,1.f,2.5f,.39f,2.15f));
    assert(!g67_wall_clear_at(f+2,1,-.2f,1.f,0.f,.39f,2.15f));
    assert(!g67_wall_clear_at(f+2,1,.2f,1.f,0.f,.39f,2.15f));
    assert(g67_wall_clear_at(f+2,1,.7f,1.f,0.f,.39f,2.15f));
    assert(g67_wall_clear_at(f+2,1,.15f,-4.f,0.f,.39f,2.15f));
    assert(!g67_wall_clear_at(f,1,500.f,0.f,0.f,.39f,2.15f));
    assert(g67_horizontal_ok(1,1,0,9.f,0.f));
    assert(!g67_horizontal_ok(0,1,0,9.f,0.f));
    assert(!g67_horizontal_ok(1,0,1,9.f,9.f));
    assert(!g67_horizontal_ok(0,1,1,9.f,0.f));
    assert(g67_horizontal_ok(0,1,1,9.f,8.85f));
    assert(g67_horizontal_ok(0,1,1,9.f,9.25f));
    puts("G67 PASS: source wall foot/head slices, vertical separation, source bounds, grounded vs flight floor policy");
    return 0;
}
