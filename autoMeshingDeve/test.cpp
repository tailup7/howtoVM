#include <iostream>
#include <gmsh.h>
#include <set>
#include <sstream>
#include <algorithm>
#include <test.h>

namespace autoMeshing {

    GmshTest::GmshTest() {
        // コンストラクタで GMSH を初期化
        gmsh::initialize();
    }

    GmshTest::~GmshTest() {
        // デストラクタで GMSH を終了
        gmsh::finalize();
    }

    void GmshTest::initializeAndGenerateMesh() {
        // モデルを追加
        gmsh::model::add("t10");

        // 単純な矩形のジオメトリを作成
        double lc = .15;
        gmsh::model::geo::addPoint(0.0, 0.0, 0, lc, 1);
        gmsh::model::geo::addPoint(1, 0.0, 0, lc, 2);
        gmsh::model::geo::addPoint(1, 1, 0, lc, 3);
        gmsh::model::geo::addPoint(0, 1, 0, lc, 4);
        gmsh::model::geo::addPoint(0.2, .5, 0, lc, 5);

        gmsh::model::geo::addLine(1, 2, 1);
        gmsh::model::geo::addLine(2, 3, 2);
        gmsh::model::geo::addLine(3, 4, 3);
        gmsh::model::geo::addLine(4, 1, 4);

        gmsh::model::geo::addCurveLoop({ 1, 2, 3, 4 }, 5);
        gmsh::model::geo::addPlaneSurface({ 5 }, 6);

        gmsh::model::geo::synchronize();

        // サイズフィールドの定義
        defineMeshSizeFields();

        // メッシュ生成
        gmsh::model::mesh::generate(2);
        gmsh::write("t10.msh");

        // GUIを表示
        gmsh::fltk::run();
    }

    void GmshTest::defineMeshSizeFields() {
        // Distance フィールドの定義
        gmsh::model::mesh::field::add("Distance", 1);
        gmsh::model::mesh::field::setNumbers(1, "PointsList", { 5 });
        gmsh::model::mesh::field::setNumbers(1, "CurvesList", { 2 });
        gmsh::model::mesh::field::setNumber(1, "Sampling", 100);

        // Threshold フィールドの定義
        gmsh::model::mesh::field::add("Threshold", 2);
        gmsh::model::mesh::field::setNumber(2, "InField", 1);
        gmsh::model::mesh::field::setNumber(2, "SizeMin", .15 / 30);
        gmsh::model::mesh::field::setNumber(2, "SizeMax", .15);
        gmsh::model::mesh::field::setNumber(2, "DistMin", 0.15);
        gmsh::model::mesh::field::setNumber(2, "DistMax", 0.5);

        // MathEval フィールドの定義
        gmsh::model::mesh::field::add("MathEval", 3);
        gmsh::model::mesh::field::setString(3, "F", "cos(4*3.14*x) * sin(4*3.14*y) / 10 + 0.101");

        // Box フィールドの定義
        gmsh::model::mesh::field::add("Box", 6);
        gmsh::model::mesh::field::setNumber(6, "VIn", .15 / 15);
        gmsh::model::mesh::field::setNumber(6, "VOut", .15);
        gmsh::model::mesh::field::setNumber(6, "XMin", 0.3);
        gmsh::model::mesh::field::setNumber(6, "XMax", 0.6);
        gmsh::model::mesh::field::setNumber(6, "YMin", 0.3);
        gmsh::model::mesh::field::setNumber(6, "YMax", 0.6);
        gmsh::model::mesh::field::setNumber(6, "Thickness", 0.3);

        // 最小値を背景メッシュサイズとして設定
        gmsh::model::mesh::field::add("Min", 7);
        gmsh::model::mesh::field::setNumbers(7, "FieldsList", { 2, 3, 5, 6 });
        gmsh::model::mesh::field::setAsBackgroundMesh(7);
    }

}