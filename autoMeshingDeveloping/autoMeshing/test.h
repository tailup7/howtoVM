#ifndef TEST_H
#define TEST_H

#include <gmsh.h>
#include <set>
#include <string>
#include <vector>

namespace autoMeshing {

    class GmshTest {
    public:
        // �R���X�g���N�^�ƃf�X�g���N�^
        GmshTest();
        ~GmshTest();

        // ���b�V�������Ə������̊֐�
        void initializeAndGenerateMesh();

    private:
        // ���b�V���T�C�Y�t�B�[���h�̒�`
        void defineMeshSizeFields();
    };

}

#endif // TEST_H