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
            // "facet"�s���������玟�̍s�ɐi��
            if (line.find("facet") != std::string::npos) {
                // "vertex"�s��T���č��W�𒊏o
                for (int i = 0; i < 3; ++i) {
                    std::getline(file, line); // "outer loop" �Ƃ� "normal" �̍s���΂�
                    if (line.find("vertex") != std::string::npos) {
                        // ��: vertex 1.0 2.0 3.0 �̌`��
                        std::istringstream vertex_stream(line);
                        std::string temp;
                        float x, y, z;
                        vertex_stream >> temp >> x >> y >> z;
                        vertices.push_back(Point3D(x, y, z));
                    }
                }
                // "endloop" �� "endfacet" ���΂�
                std::getline(file, line); // "endloop"
                std::getline(file, line); // "endfacet"
            }
        }

        file.close();
        return true;
    }


}