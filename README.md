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
        
        ![- 데이터 테이블 관계 내용](https://prod-files-secure.s3.us-west-2.amazonaws.com/9d59024f-aa47-420a-9bd6-96cc144d126c/468754ec-62e9-4801-8d11-8996d8eaa05f/Untitled.png)
        
        - 데이터 테이블 관계 내용
        
    
    - 언어 및 프레임워크
        - Python 3.8.6 : 개발 언어
        - django 3.2.16 : python 기반 웹 개발 프레임워크
        - Flask : AI 모델이 담긴 API 개발
    - 배포 및 관리
        - Github
        - vagrant (가상환경 5개 구성)
            
            ![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/9d59024f-aa47-420a-9bd6-96cc144d126c/b6254b64-1581-46b0-b23d-95d0829b9f3f/Untitled.png)
            
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

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/9d59024f-aa47-420a-9bd6-96cc144d126c/6d018354-5c88-4932-9a68-0f546aabadba/Untitled.png)

- 문진화면 - 사용자 입력

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/9d59024f-aa47-420a-9bd6-96cc144d126c/67ae1263-f5ee-44cc-9098-295b34835e32/Untitled.png)

- 문진화면 - 문진항목 입력

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/9d59024f-aa47-420a-9bd6-96cc144d126c/11fd2fab-8a7b-46aa-8ba5-4b03317c6ade/Untitled.png)

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/9d59024f-aa47-420a-9bd6-96cc144d126c/9ef9919e-89db-4a4c-a5fe-59a9708e212d/Untitled.png)

- 문진 결과화면

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/9d59024f-aa47-420a-9bd6-96cc144d126c/a7d60940-1ad7-487f-a38e-312d6c025603/Untitled.png)

- 문진 완료 및 대기자 목록 화면

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/9d59024f-aa47-420a-9bd6-96cc144d126c/0158f113-ff57-4cfb-9449-6fa061d520ba/Untitled.png)

- 설진 화면

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/9d59024f-aa47-420a-9bd6-96cc144d126c/41f3c6ea-f6cf-4081-95a8-e975fd2d25f2/Untitled.png)

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/9d59024f-aa47-420a-9bd6-96cc144d126c/c2d60d70-6294-47c2-8340-9c6a5b5ea4ca/Untitled.png)

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/9d59024f-aa47-420a-9bd6-96cc144d126c/a2e33630-da85-4857-85ae-bf6aa267c0c7/Untitled.png)

- 설진 완료 및 처방 화면

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/9d59024f-aa47-420a-9bd6-96cc144d126c/355086dc-f7d8-4f21-9109-f48329e87ce2/Untitled.png)

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/9d59024f-aa47-420a-9bd6-96cc144d126c/d4060361-b533-44a8-b5e0-251fca344198/Untitled.png)

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/9d59024f-aa47-420a-9bd6-96cc144d126c/137003d0-3ef7-41f1-b6cc-49b52e6e735f/Untitled.png)
