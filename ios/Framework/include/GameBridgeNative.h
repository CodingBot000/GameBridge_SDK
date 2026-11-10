#ifndef GAMEBRIDGE_NATIVE_H
#define GAMEBRIDGE_NATIVE_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
// Callback bytes are borrowed and must be copied before the callback returns.
typedef void (*GBCallback)(const uint8_t *bytes, int32_t length);
int32_t GB_ProtocolVersion(void);
void GB_SetCallback(GBCallback callback);
// Input bytes are copied before this function returns.
void GB_Dispatch(const uint8_t *bytes, int32_t length);
void GB_Shutdown(void);
#ifdef __cplusplus
}
#endif
#endif
