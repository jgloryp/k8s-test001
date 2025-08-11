# 멀티스테이지 빌드를 사용한 Node.js 애플리케이션
FROM node:22-alpine AS builder

WORKDIR /home/node/app

# 의존성 파일 복사 및 설치 (캐시 최적화)
COPY --chown=node:node package*.json ./
RUN npm ci --frozen-lockfile

# 소스 코드 복사 및 빌드
COPY --chown=node:node src ./src
COPY --chown=node:node tsconfig.json ./
RUN npm run build

# 프로덕션 이미지
FROM node:22-alpine AS production

# Tini 설치 (신호 처리를 위한)
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

WORKDIR /home/node/app

# 프로덕션 의존성만 설치
COPY --chown=node:node package*.json ./
RUN npm ci --frozen-lockfile --production && npm cache clean --force

# 빌드된 애플리케이션 복사
COPY --chown=node:node --from=builder /home/node/app/dist ./dist

# 헬스체크 추가 (wget 사용 - Alpine에 기본 포함)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# 애플리케이션 포트만 노출
EXPOSE 3000

# 비루트 사용자로 실행
USER node

# Tini를 entrypoint로 설정하고 Node.js 직접 실행
ENTRYPOINT ["/tini", "--"]
CMD ["node", "dist/server.js"]