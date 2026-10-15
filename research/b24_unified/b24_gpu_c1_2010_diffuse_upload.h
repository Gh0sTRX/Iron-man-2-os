#ifndef B24_GPU_C1_2010_DIFFUSE_UPLOAD_H
#define B24_GPU_C1_2010_DIFFUSE_UPLOAD_H
#include "b24_c1_2010_diffuse_bank.h"
#include "b24_c1_material_batches.h"
/* Same existing VitaGL owner/context. Loads ONCE at map open, no texture
   CPU uploading during gameplay frames. Only visible (ground/urban/cars)
   exact source-verified BRES→C1MT images. Others remain diagnostic fallback.
   Max 512x512 native RGBA downsample ONLY when source exceeds 512, CPU once
   to respect 2011 PS Vita memory. Original C1TX source bytes unchanged.
   GL textures are resources, not a second GPU renderer/swap frame. */
int b24_gpu_c1_2010_diffuse_upload(B24C1OriginalDiffuseBank *bank,
 const B24C1MaterialBatchPlan *plan,const char *asset_folder);
void b24_gpu_c1_2010_diffuse_release(B24C1OriginalDiffuseBank *bank);
#endif
