from ctypes import *

lib_dsp = CDLL('libgnsdk_dsp.so')
lib_man = CDLL('libgnsdk_manager.so')
lib_mid_stream = CDLL('libgnsdk_musicid_stream.so')

# types
gnsdk_user_handle_t = c_uint64
gnsdk_error_t = c_uint64
gnsdk_manager_handle_t = c_uint64
gnsdk_locale_handle_t = c_uint64
gnsdk_cstr_t = c_char_p
gnsdk_size_t = c_ulong
gnsdk_musicidstream_channel_handle_t = c_uint64
gnsdk_void_t = None
gnsdk_char_t = c_char
gnsdk_musicidstream_preset_t = c_uint64
gnsdk_uint32_t = c_uint64
gnsdk_byte_t = c_ubyte
gnsdk_status_t = c_uint64 # enum
gnsdk_bool_t = c_char
gnsdk_musicidstream_processing_status_t = c_uint64 # enum
gnsdk_musicidstream_identifying_status_t = c_uint64 # enum
gnsdk_gdo_handle_t = c_uint64 # guess

# constants
GNSDK_NULL = c_void_p(None)
GNSDK_SUCCESS = 0
GNSDK_MANAGER_LICENSEDATA_FILENAME = gnsdk_size_t(-2)
GNSDK_MUSICIDSTREAM_TIMEOUT_INFINITE = 2**32 - 1
GNSDK_GDO_CHILD_ALBUM = "gnsdk_ctx_album!".encode('ASCII')
GNSDK_GDO_CHILD_ARTIST = "gnsdk_ctx_artist!".encode('ASCII')
GNSDK_GDO_CHILD_TRACK = "gnsdk_ctx_track!".encode('ASCII')
GNSDK_GDO_CHILD_TITLE_OFFICIAL = "gnsdk_ctx_title!off".encode('ASCII')
GNSDK_GDO_CHILD_NAME_OFFICIAL = "gnsdk_xtc_name!off".encode('ASCII')
GNSDK_GDO_VALUE_DISPLAY = "gnsdk_val_display".encode('ASCII')
GNSDK_GDO_CHILD_TRACK_MATCHED = "gnsdk_ctx_track!matching".encode('ASCII')
GNSDK_USER_REGISTER_MODE_ONLINE = "gnsdk_userregmode_online".encode('ASCII')


class gnsdk_error_info_t(Structure):
    _fields_ = [("error_code", gnsdk_error_t),
                ("source_error_code", gnsdk_error_t),
                ("error_description", gnsdk_cstr_t),
                ("error_api", gnsdk_cstr_t),
                ("error_module", gnsdk_cstr_t),
                ("source_error_module", gnsdk_cstr_t)]

# callback function types
gnsdk_status_callback_fn_t = CFUNCTYPE(None, c_void_p, gnsdk_status_t, gnsdk_uint32_t, gnsdk_size_t, gnsdk_size_t, POINTER(gnsdk_bool_t))
gnsdk_processing_status_fn_t = CFUNCTYPE(None, POINTER(gnsdk_void_t), gnsdk_musicidstream_processing_status_t, POINTER(gnsdk_bool_t))
gnsdk_identifying_status_fn_t = CFUNCTYPE(None, POINTER(gnsdk_void_t), gnsdk_musicidstream_identifying_status_t, POINTER(gnsdk_bool_t))
gnsdk_result_available_fn_t = CFUNCTYPE(None, POINTER(gnsdk_void_t), gnsdk_musicidstream_channel_handle_t, gnsdk_gdo_handle_t, POINTER(gnsdk_bool_t))
gnsdk_callback_error_fn_t = CFUNCTYPE(None, POINTER(gnsdk_void_t), gnsdk_musicidstream_channel_handle_t, POINTER(gnsdk_error_info_t))


class gnsdk_musicidstream_callbacks_t(Structure):
    _fields_ = [("callback_status", gnsdk_status_callback_fn_t),
                ("callback_processing_status", gnsdk_processing_status_fn_t),
                ("callback_identifying_status", gnsdk_identifying_status_fn_t),
                ("callback_result_available", gnsdk_result_available_fn_t),
                ("callback_error", gnsdk_callback_error_fn_t)]

# musicstream enum
gnsdk_musicidstream_preset_invalid = gnsdk_musicidstream_preset_t(0)
gnsdk_musicidstream_preset_microphone = gnsdk_musicidstream_preset_t(1)
gnsdk_musicidstream_preset_radio = gnsdk_musicidstream_preset_t(2)

# functions
gnsdk_manager_initialize = lib_man.gnsdk_manager_initialize
gnsdk_manager_initialize.restype = gnsdk_error_t
gnsdk_manager_initialize.argtypes = [POINTER(gnsdk_manager_handle_t), POINTER(gnsdk_char_t), gnsdk_size_t]

gnsdk_musicidstream_initialize = lib_mid_stream.gnsdk_musicidstream_initialize
gnsdk_musicidstream_initialize.restype = gnsdk_error_t
gnsdk_musicidstream_initialize.argtypes = [gnsdk_manager_handle_t]

gnsdk_manager_locale_load = lib_man.gnsdk_manager_locale_load
gnsdk_manager_locale_load.restype = gnsdk_error_t
gnsdk_manager_locale_load.argtypes = [gnsdk_cstr_t, gnsdk_cstr_t, gnsdk_cstr_t, gnsdk_cstr_t, gnsdk_user_handle_t, c_void_p, POINTER(gnsdk_void_t), POINTER(gnsdk_locale_handle_t)]

gnsdk_manager_locale_set_group_default = lib_man.gnsdk_manager_locale_set_group_default
gnsdk_manager_locale_set_group_default.restype = gnsdk_error_t
gnsdk_manager_locale_set_group_default.argtypes = [gnsdk_locale_handle_t]

gnsdk_manager_locale_release = lib_man.gnsdk_manager_locale_release
gnsdk_manager_locale_release.restype = gnsdk_error_t
gnsdk_manager_locale_release.argtypes = [gnsdk_locale_handle_t]

gnsdk_manager_user_create = lib_man.gnsdk_manager_user_create
gnsdk_manager_user_create.restype = gnsdk_error_t
gnsdk_manager_user_create.argtypes = [gnsdk_cstr_t, gnsdk_cstr_t, POINTER(gnsdk_user_handle_t)]

gnsdk_manager_user_release = lib_man.gnsdk_manager_user_release
gnsdk_manager_user_release.restype = gnsdk_error_t
gnsdk_manager_user_release.argtypes = [gnsdk_user_handle_t]

gnsdk_manager_user_register = lib_man.gnsdk_manager_user_register
gnsdk_manager_user_register.restype = gnsdk_error_t
gnsdk_manager_user_register.argtypes = [gnsdk_cstr_t, gnsdk_cstr_t, gnsdk_cstr_t, gnsdk_cstr_t, POINTER(gnsdk_cstr_t)]

gnsdk_manager_shutdown = lib_man.gnsdk_manager_shutdown
gnsdk_manager_shutdown.restype = gnsdk_error_t
gnsdk_manager_shutdown.argtypes = []

gnsdk_dsp_initialize = lib_dsp.gnsdk_dsp_initialize
gnsdk_dsp_initialize.restype = gnsdk_error_t
gnsdk_dsp_initialize.argtypes = [gnsdk_manager_handle_t]

gnsdk_musicidstream_channel_create = lib_mid_stream.gnsdk_musicidstream_channel_create
gnsdk_musicidstream_channel_create.restype = gnsdk_error_t
gnsdk_musicidstream_channel_create.argtypes = [gnsdk_user_handle_t, gnsdk_musicidstream_preset_t, POINTER(gnsdk_musicidstream_callbacks_t), POINTER(gnsdk_void_t), POINTER(gnsdk_musicidstream_channel_handle_t)]

gnsdk_musicidstream_channel_release = lib_mid_stream.gnsdk_musicidstream_channel_release
gnsdk_musicidstream_channel_release.restype = gnsdk_error_t
gnsdk_musicidstream_channel_release.argtypes = [gnsdk_musicidstream_channel_handle_t]

# second argument is waittime in ms
gnsdk_musicidstream_channel_wait_for_identify = lib_mid_stream.gnsdk_musicidstream_channel_wait_for_identify
gnsdk_musicidstream_channel_wait_for_identify.retype = gnsdk_error_t
gnsdk_musicidstream_channel_wait_for_identify.argtypes = [gnsdk_musicidstream_channel_handle_t, gnsdk_uint32_t]

gnsdk_musicidstream_channel_audio_begin = lib_mid_stream.gnsdk_musicidstream_channel_audio_begin
gnsdk_musicidstream_channel_audio_begin.restype = gnsdk_error_t
gnsdk_musicidstream_channel_audio_begin.argtypes = [gnsdk_user_handle_t, gnsdk_uint32_t, gnsdk_uint32_t, gnsdk_uint32_t]

gnsdk_musicidstream_channel_audio_end = lib_mid_stream.gnsdk_musicidstream_channel_audio_end
gnsdk_musicidstream_channel_audio_end.restype = gnsdk_error_t
gnsdk_musicidstream_channel_audio_end.argtypes = [gnsdk_musicidstream_channel_handle_t]

gnsdk_musicidstream_channel_identify = lib_mid_stream.gnsdk_musicidstream_channel_identify
gnsdk_musicidstream_channel_identify.restype = gnsdk_error_t
gnsdk_musicidstream_channel_identify.argtypes = [gnsdk_musicidstream_channel_handle_t]

gnsdk_musicidstream_channel_audio_write = lib_mid_stream.gnsdk_musicidstream_channel_audio_write
gnsdk_musicidstream_channel_audio_write.restype = gnsdk_error_t
gnsdk_musicidstream_channel_audio_write.argtypes = [gnsdk_musicidstream_channel_handle_t, POINTER(gnsdk_byte_t), gnsdk_size_t]

gnsdk_manager_gdo_child_count = lib_man.gnsdk_manager_gdo_child_count
gnsdk_manager_gdo_child_count.restype = gnsdk_error_t
gnsdk_manager_gdo_child_count.argtypes = [gnsdk_gdo_handle_t, gnsdk_cstr_t, POINTER(gnsdk_uint32_t)]

gnsdk_manager_gdo_value_get = lib_man.gnsdk_manager_gdo_value_get
gnsdk_manager_gdo_value_get.restype = gnsdk_error_t
gnsdk_manager_gdo_value_get.argtypes = [gnsdk_gdo_handle_t, gnsdk_cstr_t, gnsdk_uint32_t, POINTER(gnsdk_cstr_t)]

gnsdk_manager_gdo_child_get = lib_man.gnsdk_manager_gdo_child_get
gnsdk_manager_gdo_child_get.restype = gnsdk_error_t
gnsdk_manager_gdo_child_get.argtypes = [gnsdk_gdo_handle_t, gnsdk_cstr_t, gnsdk_uint32_t, POINTER(gnsdk_gdo_handle_t)]

gnsdk_manager_gdo_value_get = lib_man.gnsdk_manager_gdo_value_get
gnsdk_manager_gdo_value_get.restype = gnsdk_error_t
gnsdk_manager_gdo_value_get.argtypes = [gnsdk_gdo_handle_t, gnsdk_cstr_t, gnsdk_uint32_t, POINTER(gnsdk_cstr_t)]

gnsdk_manager_gdo_render = lib_man.gnsdk_manager_gdo_render
gnsdk_manager_gdo_render.restype = gnsdk_error_t
gnsdk_manager_gdo_render.argtypes = [gnsdk_gdo_handle_t, gnsdk_uint32_t, POINTER(c_char_p)]
