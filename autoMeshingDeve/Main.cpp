#include <iostream>
#include <console.h>
#include <test.h>

int main()
{
    autoMeshing::test();

    autoMeshing::GmshTest gmshTest;
    gmshTest.initializeAndGenerateMesh();

    return 0;
}

