#include <stl.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <iomanip>

namespace autoMeshing {

    bool readSTL(const std::string& filename, std::vector<Point3D>& vertices) {
        std::ifstream file(filename);
        if (!file.is_open()) {
            std::cerr << "Error opening file: " << filename << std::endl;
            return false;
        }

        std::string line;
        while (std::getline(file, line)) {
            // "facet"行を見つけたら次の行に進む
            if (line.find("facet") != std::string::npos) {
                // "vertex"行を探して座標を抽出
                for (int i = 0; i < 3; ++i) {
                    std::getline(file, line); // "outer loop" とか "normal" の行を飛ばす
                    if (line.find("vertex") != std::string::npos) {
                        // 例: vertex 1.0 2.0 3.0 の形式
                        std::istringstream vertex_stream(line);
                        std::string temp;
                        float x, y, z;
                        vertex_stream >> temp >> x >> y >> z;
                        vertices.push_back(Point3D(x, y, z));
                    }
                }
                // "endloop" と "endfacet" を飛ばす
                std::getline(file, line); // "endloop"
                std::getline(file, line); // "endfacet"
            }
        }

        file.close();
        return true;
    }


}