- **개요**
    - 한의원에서는 환자들의 생활 습관을 묻는 문진을 통해 상태를 진단하고, 처방약을 처방함.
    - 또한, 혀를 보고 건강상태를 진단하는 설진을 통해 진단에 참고할 수 있음.
    - AI 문진 및 설진 분석 서비스는 사용자가 위 2개의 진단을 자동적으로 종합하고, 처방할 수 있는 서비스를 제공하는 시스템을 개발함.
    
- Use-case (Brief)
    - Actor : 환자, 한의사
    - Scenario
        - (환자 사용자) ‘사용자 정보’를 입력하고, 문진 내용을 입력하고, AI 결과를 확인함.
        - (한의사 사용자) 문진 완료 환자를 목록에서 확인하고, 설진 화면 진입하여 혀 사진을 업로드하고, AI 분석 결과를 확인함.
        - (한의사 사용자) 처방 화면에서 문진과 설진을 종합한 처방 내용을 확인하고, 처방약을 선택할 수 있고, 이 내용을 프린트 함.

- 개발 환경 및 활용 사례
    - 데이터 베이스
        - postgresDB 3.2.16 : 사용자 정보, 문진 및 설진 정보 데이터 적재
        
        ![스크린샷 2024-01-29 104541](https://github.com/yeongtaekjeong/detox_system/assets/147578834/439f6f0f-36c4-458a-9a36-5e1c8251d32a)
        
    - 언어 및 프레임워크
        - Python 3.8.6 : 개발 언어
        - django 3.2.16 : python 기반 웹 개발 프레임워크
        - Flask : AI 모델이 담긴 API 개발
    - 배포 및 관리
        - Github
        - vagrant (가상환경 5개 구성)
            ![스크린샷 2024-01-29 104547](https://github.com/yeongtaekjeong/detox_system/assets/147578834/d1018867-67ff-4cfb-a9b4-19be0a267d8a)
            
        - Ubuntu 20.04
        - nginx(WAS)
        - gunicorn(wsgi)

- 개발 내용
    - 개발 참여 인원 : 3명
    - 본인 담당 업무
        - 문진 데이터의 분류, 회귀 모델 개발 및 Flask API 구축
            
            - 라벨링 된 실제 문진 데이터 15,000row 활용
            
            - 전처리 : pandas, numpy 등
            
            - 회귀, 분류에 XGboost 알고리즘 사용
            
            - 분류 성능(F1-score) : 0.95, 회귀 성능(mse) : 0.90
            
        - Django 프레임워크 활용 화면 개발 : 메인화면, 문진화면, 처방화면
        - 담당 화면의 데이터베이스 CRUD 기능 구현
        - 가상환경 내 Ubuntu 서버에 배포 및 도메인 적용

- 메인화면
![스크린샷 2024-01-29 104555](https://github.com/yeongtaekjeong/detox_system/assets/147578834/b8ac89e1-7e65-451f-b866-f5f2be08a3ef)

- 문진화면 - 사용자 입력
![스크린샷 2024-01-29 104600](https://github.com/yeongtaekjeong/detox_system/assets/147578834/df7aae05-8034-4907-b600-1ef9155f6f26)


- 문진화면 - 문진항목 입력
![스크린샷 2024-01-29 104607](https://github.com/yeongtaekjeong/detox_system/assets/147578834/08d4395d-ab5d-415a-8791-2a2d45340617)
![스크린샷 2024-01-29 104612](https://github.com/yeongtaekjeong/detox_system/assets/147578834/0b6a03a3-72d8-442a-9627-05b60a8ab261)


- 문진 결과화면
![스크린샷 2024-01-29 104617](https://github.com/yeongtaekjeong/detox_system/assets/147578834/d9e35242-ef88-486b-81a2-c38d79fc5bec)


- 문진 완료 및 대기자 목록 화면
![스크린샷 2024-01-29 104622](https://github.com/yeongtaekjeong/detox_system/assets/147578834/f1bc26b4-f9ea-41f6-baea-cc7054e8742b)


- 설진 화면
![스크린샷 2024-01-29 104630](https://github.com/yeongtaekjeong/detox_system/assets/147578834/18621905-9efa-4c24-adf6-71e980af4119)


- 설진 완료 및 처방 화면
![스크린샷 2024-01-29 104646](https://github.com/yeongtaekjeong/detox_system/assets/147578834/c5a5fecc-4b39-4368-a0b6-79263e8510e9)

![스크린샷 2024-01-29 104652](https://github.com/yeongtaekjeong/detox_system/assets/147578834/537555b1-c289-4e85-a2ef-823e25aa6e39)

![스크린샷 2024-01-29 104657](https://github.com/yeongtaekjeong/detox_system/assets/147578834/1b809ade-1ae9-4ac0-9e84-cb9d379a01de)



