qt_add_library(lib2)
target_sources(lib2 PRIVATE
    lib2.cpp
)
target_link_libraries(lib2 PUBLIC
    Qt::Core
    Qt::Gui
)

# install_lib
install(TARGETS lib2
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FRAMEWORK DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
