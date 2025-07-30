
# 1. 기본 이미지 선택 (Node.js 16)
FROM node:16-alpine

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. package.json 복사
COPY package.json . 

# 4. 의존성 설치
RUN set -ex && npm install

# 5. 소스 코드 복사
COPY . .

# 6. React 앱 빌드
RUN set -ex && npm run build || exit 1

# 빌드 결과 확인 (디버깅용)
RUN ls -la build
RUN cat build/index.html

# 7. 서빙을 위한 웹서버 설치
RUN npm install -g serve

# 8. 포트 노출
EXPOSE 3000

# 9. 앱 실행
CMD ["serve", "-s", "build", "-l", "3000"]
