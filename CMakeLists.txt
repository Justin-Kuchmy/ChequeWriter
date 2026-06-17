    cmake_minimum_required(VERSION 3.16)

    project(JustPay LANGUAGES CXX)

    set(CMAKE_CXX_STANDARD 20)
    set(CMAKE_CXX_STANDARD_REQUIRED ON)

    # ---------------------------------------------------------
    # Qt Setup
    # ---------------------------------------------------------

    find_package(Qt6 REQUIRED COMPONENTS 
        Core
        Gui 
        Qml
        Widgets 
        Quick 
        QuickWidgets 
        Sql 
        PrintSupport)
    
    set(CMAKE_AUTOMOC ON)
    set(CMAKE_AUTOUIC ON)
    set(CMAKE_AUTORCC ON)
    set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
    
    if((MINGW OR UNIX) AND CMAKE_BUILD_TYPE STREQUAL "Debug")
        add_compile_options(
            -ggdb
            -Wall
            -Wextra
            -pedantic-errors
            -Wno-unused-parameter
        )
    endif()
   
        
        
    # ---------------------------------------------------------
    # Shared source files for all builds
    # ---------------------------------------------------------
    file(GLOB_RECURSE APP_SOURCES CONFIGURE_DEPENDS
        "${CMAKE_SOURCE_DIR}/main_qt.cpp"
        "${CMAKE_SOURCE_DIR}/Source/*.cpp"
        "${CMAKE_SOURCE_DIR}/UI/*.cpp"
        )

    file(GLOB_RECURSE HEADER_FILES CONFIGURE_DEPENDS
    "${CMAKE_SOURCE_DIR}/Include/*.h"
    )

    # Collect UI files
    file(GLOB_RECURSE UI_FILES
    "${CMAKE_SOURCE_DIR}/UI/*.ui"
    )

    # ---------------------------------------------------------
    # Include resource file if it exists
    # ---------------------------------------------------------
    set(RESOURCE_FILE "${CMAKE_SOURCE_DIR}/Resources/resources.qrc")

    if(EXISTS ${RESOURCE_FILE})
        list(APPEND APP_SOURCES ${RESOURCE_FILE})
        endif()
    
    #---------------------------------------------------------
    #=== MAIN APP TARGET ===
    #----------------------------------------------------------
    add_executable(JustPay
    ${APP_SOURCES}
    ${HEADER_FILES}
    ${UI_FILES}
    )
    
    # ---------------------------------------------------------
    # Include directories
    # ---------------------------------------------------------
    target_include_directories(JustPay PRIVATE
    ${CMAKE_SOURCE_DIR}/Include
    )

    set(CMAKE_AUTOUIC_OUTPUT_DIR "${CMAKE_BINARY_DIR}/Generated")


    set_target_properties(JustPay PROPERTIES AUTOUIC_SEARCH_PATHS "${CMAKE_SOURCE_DIR}/UI/Dialogs")

    

# ---------------------------------------------------------
# Link Qt and SQLite libraries
# ---------------------------------------------------------

    if(WIN32)

        if(EXISTS "C:/Libraries/curl")
            set(CURL_ROOT "C:/Libraries/curl")
        endif()

        # GitHub Actions MSYS2 path
        if(EXISTS "C:/tools/msys64/mingw64")
            list(APPEND CMAKE_PREFIX_PATH
                "C:/tools/msys64/mingw64"
            )
        endif()

    endif()

    find_package(CURL REQUIRED)
    find_package(SQLite3 REQUIRED)

    target_link_libraries(JustPay
        PRIVATE
            Qt6::Core
            Qt6::Gui
            Qt6::Widgets
            Qt6::Qml
            Qt6::Quick
            Qt6::QuickWidgets
            Qt6::Sql 
            Qt6::PrintSupport
            
            SQLite::SQLite3
            CURL::libcurl
    )


set_property(GLOBAL PROPERTY USE_FOLDERS ON)
set_target_properties(JustPay PROPERTIES FOLDER "Apps")

# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------
if(BUILD_TESTS)
    add_subdirectory(Tests)
endif()