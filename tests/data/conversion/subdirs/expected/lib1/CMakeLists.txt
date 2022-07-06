qt_add_library(lib1)
target_sources(lib1 PRIVATE
    lib1/lib1.cpp
)
target_link_libraries(lib1 PUBLIC
    Qt::Core
    Qt::Gui
    Qt::Network
)

# install_lib
install(TARGETS lib1
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FRAMEWORK DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
