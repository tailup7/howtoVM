#include <iostream>
#include <console.h>
#include <test.h>
#include <stl.h>

int main()
{
    autoMeshing::writeHello();

    autoMeshing::GmshTest gmshTest;
    gmshTest.initializeAndGenerateMesh();

    std::string filename = "input.stl";

    std::vector<autoMeshing::Point3D> vertices;

    // STLファイルを読み込み
    if (!readSTL(filename, vertices)) {
        return 1;
    }

    // 読み込んだ頂点の総数を表示
    std::cout << "Total number of vertices in the STL: " << vertices.size() << std::endl;


    // 読み込んだ頂点の座標を表示
    //std::cout << "Vertices in the STL file:" << std::endl;
    //for (const auto& vertex : vertices) {
    //    std::cout << "x: " << vertex.x << ", y: " << vertex.y << ", z: " << vertex.z << std::endl;
    //}

    return 0;
}

