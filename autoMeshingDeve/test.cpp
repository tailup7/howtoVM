#include <iostream>
#include <gmsh.h>
#include <set>
#include <sstream>
#include <algorithm>
#include <test.h>

namespace autoMeshing {

    GmshTest::GmshTest() {
        // �R���X�g���N�^�� GMSH ��������
        gmsh::initialize();
    }

    GmshTest::~GmshTest() {
        // �f�X�g���N�^�� GMSH ���I��
        gmsh::finalize();
    }

    void GmshTest::initializeAndGenerateMesh() {
        // ���f����ǉ�
        gmsh::model::add("t10");

        // �P���ȋ�`�̃W�I���g�����쐬
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

        // �T�C�Y�t�B�[���h�̒�`
        defineMeshSizeFields();

        // ���b�V������
        gmsh::model::mesh::generate(2);
        gmsh::write("t10.msh");

        // GUI��\��
        gmsh::fltk::run();
    }

    void GmshTest::defineMeshSizeFields() {
        // Distance �t�B�[���h�̒�`
        gmsh::model::mesh::field::add("Distance", 1);
        gmsh::model::mesh::field::setNumbers(1, "PointsList", { 5 });
        gmsh::model::mesh::field::setNumbers(1, "CurvesList", { 2 });
        gmsh::model::mesh::field::setNumber(1, "Sampling", 100);

        // Threshold �t�B�[���h�̒�`
        gmsh::model::mesh::field::add("Threshold", 2);
        gmsh::model::mesh::field::setNumber(2, "InField", 1);
        gmsh::model::mesh::field::setNumber(2, "SizeMin", .15 / 30);
        gmsh::model::mesh::field::setNumber(2, "SizeMax", .15);
        gmsh::model::mesh::field::setNumber(2, "DistMin", 0.15);
        gmsh::model::mesh::field::setNumber(2, "DistMax", 0.5);

        // MathEval �t�B�[���h�̒�`
        gmsh::model::mesh::field::add("MathEval", 3);
        gmsh::model::mesh::field::setString(3, "F", "cos(4*3.14*x) * sin(4*3.14*y) / 10 + 0.101");

        // Box �t�B�[���h�̒�`
        gmsh::model::mesh::field::add("Box", 6);
        gmsh::model::mesh::field::setNumber(6, "VIn", .15 / 15);
        gmsh::model::mesh::field::setNumber(6, "VOut", .15);
        gmsh::model::mesh::field::setNumber(6, "XMin", 0.3);
        gmsh::model::mesh::field::setNumber(6, "XMax", 0.6);
        gmsh::model::mesh::field::setNumber(6, "YMin", 0.3);
        gmsh::model::mesh::field::setNumber(6, "YMax", 0.6);
        gmsh::model::mesh::field::setNumber(6, "Thickness", 0.3);

        // �ŏ��l��w�i���b�V���T�C�Y�Ƃ��Đݒ�
        gmsh::model::mesh::field::add("Min", 7);
        gmsh::model::mesh::field::setNumbers(7, "FieldsList", { 2, 3, 5, 6 });
        gmsh::model::mesh::field::setAsBackgroundMesh(7);
    }

}