## COMMON ##
include(FetchContent)

option(ENABLE_GL1 "Build OpenGL 1 renderer." ON)
option(ENABLE_GL3 "Build OpenGL 3 renderer." ON)
option(ENABLE_GLES2 "Configure OpenGL 3 renderer to be OpenGL ES 2.0 compatible." OFF)

if(NOT APPLE AND NOT WIN32 OR MINGW)
	if(NOT EMSCRIPTEN)
		find_package(PkgConfig REQUIRED)
	endif()
endif()

if(EMSCRIPTEN)
	set(ENABLE_GL1 OFF)
	set(ENABLE_GL3 ON)
	set(ENABLE_GLES2 ON)
endif()

## utf8.h ##
find_path(UTF8_INCLUDE_DIR NAMES "utf8.h" PATH_SUFFIXES "utf8")
if(NOT UTF8_INCLUDE_DIR)
	FetchContent_Declare(utf8
		GIT_REPOSITORY https://github.com/sheredom/utf8.h.git
		GIT_TAG 3e9e3ec15c7bf129664ab2a113eb03b54ee0b584
	)
	FetchContent_MakeAvailable(utf8)
	set(UTF8_INCLUDE_DIR ${utf8_SOURCE_DIR})
endif()

## zlib ##
if(EMSCRIPTEN)
	set(ZLIB_INCLUDE_DIRS "")
	set(ZLIB_LIBRARIES "")
else()
	if(WIN32)
		set(ZLIB_USE_STATIC_LIBS ON CACHE BOOL "While finding system-provided zlib look for static one")
	endif()
	find_package(ZLIB)
	if(NOT ZLIB_FOUND)
		FetchContent_Declare(zlib_fetch
			GIT_REPOSITORY https://github.com/madler/zlib.git
			GIT_TAG 51b7f2abdade71cd9bb0e7a373ef2610ec6f9daf
		)
		FetchContent_GetProperties(zlib_fetch)
		if(NOT zlib_fetch_POPULATED)
			FetchContent_Populate(zlib_fetch)
			execute_process(COMMAND sed "/^# Example binaries$/,$d" -i ${zlib_fetch_SOURCE_DIR}/CMakeLists.txt)
			set(SKIP_INSTALL_FILES YES)
			set(SKIP_INSTALL_HEADERS NO)
			add_subdirectory(${zlib_fetch_SOURCE_DIR} ${zlib_fetch_BINARY_DIR})
		endif()
		if(WIN32)
			set(ZLIB_LIBRARIES zlibstatic CACHE INTERNAL "zlib library")
		else()
			set(ZLIB_LIBRARIES z CACHE INTERNAL "zlib library")
		endif()
		set(ZLIB_INCLUDE_DIRS ${zlib_fetch_SOURCE_DIR} ${zlib_fetch_BINARY_DIR})
	endif()
endif()

## SQLite3 ##
if(EMSCRIPTEN)
	add_library(SQLite::SQLite3 INTERFACE IMPORTED)
	target_link_options(SQLite::SQLite3 INTERFACE "-s USE_SQLITE3=1")
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -s USE_SQLITE3=1")
else()
	find_package(SQLite3)
	if(NOT SQLITE3_FOUND)
		add_subdirectory(sqlite3)
	endif()
endif()

## glad ##
FetchContent_Declare(glad
	GIT_REPOSITORY https://github.com/Dav1dde/glad.git
	GIT_TAG 73db193f853e2ee079bf3ca8a64aa2eaf6459043
)
FetchContent_MakeAvailable(glad)
set(GLAD_SOURCES_DIR "${glad_SOURCE_DIR}")
add_subdirectory(${glad_SOURCE_DIR}/cmake ${CMAKE_BINARY_DIR}/glad_cmake)

if(ENABLE_GL1 OR ENABLE_GL3)
	glad_add_library(glad_gl REPRODUCIBLE API gl:compatibility=3.2 EXTENSIONS NONE)
endif()
if(ENABLE_GLES2)
	glad_add_library(glad_gles REPRODUCIBLE API gles2=2.0 EXTENSIONS GL_OES_element_index_uint GL_EXT_texture_format_BGRA8888 GL_OES_vertex_array_object)
endif()

## SDL2 ##
if(EMSCRIPTEN)
	add_library(SDL2::SDL2 INTERFACE IMPORTED)
	add_library(SDL2::SDL2main INTERFACE IMPORTED)
	add_definitions(-DENABLE_SDL2)
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -s USE_SDL=2")
else()
	find_package(SDL2 REQUIRED CONFIG)
	add_definitions(-DENABLE_SDL2)
	if(NOT TARGET SDL2::SDL2)
		add_library(SDL2::SDL2 SHARED IMPORTED)
		find_library(SDL2_LIBRARY SDL2)
		set_target_properties(SDL2::SDL2 PROPERTIES
			IMPORTED_LOCATION ${SDL2_LIBRARY}
			INTERFACE_INCLUDE_DIRECTORIES ${SDL2_INCLUDE_DIRS})
		find_library(SDL2MAIN_LIBRARY SDL2main)
		if(SDL2MAIN_LIBRARY)
			add_library(SDL2::SDL2main STATIC IMPORTED)
			set_target_properties(SDL2::SDL2main PROPERTIES
				IMPORTED_LOCATION ${SDL2MAIN_LIBRARY}
				INTERFACE_INCLUDE_DIRECTORIES ${SDL2_INCLUDE_DIRS})
		else()
			add_library(SDL2::SDL2main INTERFACE IMPORTED)
		endif()
	endif()
endif()

## imgui ##
FetchContent_Declare(imgui
	GIT_REPOSITORY https://github.com/ocornut/imgui.git
	GIT_TAG 8936b58fe26e8c3da834b8f60b06511d537b4c63
)
FetchContent_MakeAvailable(imgui)

# workaround for OpenGL includes — patch fetched sources in place (writable in build/_deps)
file(READ "${imgui_SOURCE_DIR}/backends/imgui_impl_opengl2.cpp" _opengl2_src)
string(REPLACE "OpenGL/gl.h" "glad/gl.h" _opengl2_src "${_opengl2_src}")
string(REPLACE "GL/gl.h" "glad/gl.h" _opengl2_src "${_opengl2_src}")
file(WRITE "${imgui_SOURCE_DIR}/backends/imgui_impl_opengl2.cpp" "${_opengl2_src}")

file(READ "${imgui_SOURCE_DIR}/backends/imgui_impl_opengl3.cpp" _opengl3_src)
string(REPLACE "GLES2/gl2.h" "glad/gles2.h" _opengl3_src "${_opengl3_src}")
string(REPLACE "GLES2/gl2ext.h" "glad/gles2.h" _opengl3_src "${_opengl3_src}")
string(REPLACE "GLES3/gl3.h" "glad/gles2.h" _opengl3_src "${_opengl3_src}")
file(WRITE "${imgui_SOURCE_DIR}/backends/imgui_impl_opengl3.cpp" "${_opengl3_src}")

set(IMGUI_SOURCES
	${imgui_SOURCE_DIR}/imgui.cpp
	${imgui_SOURCE_DIR}/imgui_draw.cpp
	${imgui_SOURCE_DIR}/imgui_tables.cpp
	${imgui_SOURCE_DIR}/imgui_widgets.cpp
	${imgui_SOURCE_DIR}/misc/cpp/imgui_stdlib.cpp
	${imgui_SOURCE_DIR}/backends/imgui_impl_sdl2.cpp
)
if(ENABLE_GL1)
	list(APPEND IMGUI_SOURCES ${imgui_SOURCE_DIR}/backends/imgui_impl_opengl2.cpp)
endif()
if(ENABLE_GL3)
	list(APPEND IMGUI_SOURCES ${imgui_SOURCE_DIR}/backends/imgui_impl_opengl3.cpp)
endif()

add_library(imgui STATIC ${IMGUI_SOURCES})
target_compile_definitions(imgui PUBLIC "-DImDrawIdx=unsigned int")
target_compile_definitions(imgui PUBLIC "-DIMGUI_IMPL_OPENGL_LOADER_GLAD")
if(ENABLE_GLES2)
	target_compile_definitions(imgui PUBLIC "-DIMGUI_IMPL_OPENGL_ES2")
endif()
target_include_directories(imgui PUBLIC
	${imgui_SOURCE_DIR}
	${imgui_SOURCE_DIR}/examples
	${imgui_SOURCE_DIR}/misc/cpp
)
if(ENABLE_GLES2)
	target_link_libraries(imgui glad_gles)
elseif(ENABLE_GL1 OR ENABLE_GL3)
	target_link_libraries(imgui glad_gl)
endif()
if(MINGW)
	target_link_libraries(imgui SDL2::SDL2-static)
else()
	target_link_libraries(imgui SDL2::SDL2)
endif()

## filesystem ##
message(CHECK_START "Checking for std::filesystem")
if(APPLE AND DEFINED CMAKE_OSX_DEPLOYMENT_TARGET AND CMAKE_OSX_DEPLOYMENT_TARGET VERSION_LESS "10.15")
	message(CHECK_FAIL "not available (macOS ${CMAKE_OSX_DEPLOYMENT_TARGET}), using ghc::filesystem")
	FetchContent_Declare(ghcfilesystem
		GIT_REPOSITORY https://github.com/gulrak/filesystem.git
		GIT_TAG 3f1c185ab414e764c694b8171d1c4d8c5c437517
	)
	FetchContent_MakeAvailable(ghcfilesystem)
	set(FILESYSTEM_LIBRARIES ghc_filesystem)
elseif(((CMAKE_CXX_COMPILER_ID STREQUAL "Clang" OR CMAKE_CXX_COMPILER_ID STREQUAL "GNU") AND CMAKE_CXX_COMPILER_VERSION VERSION_GREATER 9.0)
	OR (CMAKE_CXX_COMPILER_ID STREQUAL "AppleClang" AND CMAKE_CXX_COMPILER_VERSION VERSION_GREATER 11.4))
	message(CHECK_PASS "available")
	set(CMAKE_CXX_STANDARD 17)
	set(FILESYSTEM_LIBRARIES)
	add_definitions(-DWITH_STD_FILESYSTEM)
elseif((CMAKE_CXX_COMPILER_ID STREQUAL "Clang" AND CMAKE_CXX_COMPILER_VERSION VERSION_GREATER 8.0)
	OR (CMAKE_CXX_COMPILER_ID STREQUAL "AppleClang" AND CMAKE_CXX_COMPILER_VERSION VERSION_GREATER 11.0))
	message(CHECK_PASS "available")
	set(CMAKE_CXX_STANDARD 17)
	set(FILESYSTEM_LIBRARIES lc++fs)
	add_definitions(-DWITH_STD_FILESYSTEM)
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" AND CMAKE_CXX_COMPILER_VERSION VERSION_GREATER 8.0)
	message(CHECK_PASS "available")
	set(CMAKE_CXX_STANDARD 17)
	set(FILESYSTEM_LIBRARIES stdc++fs)
	add_definitions(-DWITH_STD_FILESYSTEM)
else()
	message(CHECK_FAIL "not available, using ghc::filesystem")
	FetchContent_Declare(ghcfilesystem
		GIT_REPOSITORY https://github.com/gulrak/filesystem.git
		GIT_TAG 3f1c185ab414e764c694b8171d1c4d8c5c437517
	)
	FetchContent_MakeAvailable(ghcfilesystem)
	set(FILESYSTEM_LIBRARIES ghc_filesystem)
endif()

## stb ##
if(NOT APPLE AND NOT WIN32 OR MINGW)
	if(NOT EMSCRIPTEN)
		pkg_check_modules(STB stb)
	endif()
endif()
if(NOT STB_FOUND)
	find_path(STB_INCLUDE_DIRS NAMES "stb_image.h" HINTS ${STB_INCLUDE_DIRS} PATH_SUFFIXES "stb")
endif()
if(STB_INCLUDE_DIRS)
	add_definitions(${STB_CFLAGS_OTHER})
	include_directories(${STB_INCLUDE_DIRS})
else()
	FetchContent_Declare(stb
		GIT_REPOSITORY https://github.com/nothings/stb.git
		GIT_TAG f54acd4e13430c5122cab4ca657705c84aa61b08
	)
	FetchContent_MakeAvailable(stb)
	include_directories(${stb_SOURCE_DIR})
endif()
add_definitions(-DSTBI_FAILURE_USERMSG)

## mpc - Micro Parser Combinators ##
FetchContent_Declare(mpc_fetch
	GIT_REPOSITORY https://github.com/orangeduck/mpc.git
	GIT_TAG 65f20a1a0b3249a475efa8ecb7b5ecd2c1c071c4
)
FetchContent_MakeAvailable(mpc_fetch)
add_library(mpc STATIC "${mpc_fetch_SOURCE_DIR}/mpc.c")
target_include_directories(mpc PUBLIC ${mpc_fetch_SOURCE_DIR})

## OpenBoardView ##
add_subdirectory(openboardview)
