qt_add_library(lib3)
target_sources(lib3 PRIVATE
    lib3/lib3.cpp
)
target_link_libraries(lib3 PUBLIC
    Qt::Core
    Qt::Gui
)

if(WIN32)
    target_link_libraries(lib3 PUBLIC
        Qt::Core5Compat
    )
endif()

# install_lib
install(TARGETS lib3
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FRAMEWORK DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
