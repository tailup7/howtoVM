#ifndef TEST_H
#define TEST_H

#include <gmsh.h>
#include <set>
#include <string>
#include <vector>

namespace autoMeshing {

    class GmshTest {
    public:
        // コンストラクタとデストラクタ
        GmshTest();
        ~GmshTest();

        // メッシュ生成と初期化の関数
        void initializeAndGenerateMesh();

    private:
        // メッシュサイズフィールドの定義
        void defineMeshSizeFields();
    };

}

#endif // TEST_H