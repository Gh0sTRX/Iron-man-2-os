#ifndef IM2_FAKE_AUDIOOUT_H
#define IM2_FAKE_AUDIOOUT_H
typedef int SceAudioOutChannelFlag;
#define SCE_AUDIO_OUT_PORT_TYPE_BGM 1
#define SCE_AUDIO_OUT_PORT_TYPE_MAIN 0
#define SCE_AUDIO_OUT_MODE_STEREO 0
#define SCE_AUDIO_VOLUME_FLAG_L_CH 1
#define SCE_AUDIO_VOLUME_FLAG_R_CH 2
int sceAudioOutOpenPort(int,int,int,int);
int sceAudioOutSetVolume(int,SceAudioOutChannelFlag,int *);
int sceAudioOutReleasePort(int);
#endif
