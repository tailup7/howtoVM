#ifndef STL_H
#define STL_H

#include <vector>
#include <string>

namespace autoMeshing {
    // 3D座標を保持する構造体
    struct Point3D {
        float x, y, z;

        Point3D(float x_ = 0, float y_ = 0, float z_ = 0) : x(x_), y(y_), z(z_) {}
    };

    // STLファイルを読み込んで頂点リストを作成する関数
    bool readSTL(const std::string& filename, std::vector<Point3D>& vertices);

#endif // STL_H


}


