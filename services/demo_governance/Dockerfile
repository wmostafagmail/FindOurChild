FROM --platform=linux/amd64 python:3.13.13-bookworm@sha256:2383bb1108fe80f7191b1f3ddbbd2ce1a13a1e99e7400a42fa28b27defa34841 AS build
COPY supervisor.cpp synthetic_probe.cpp /build/
RUN --network=none mkdir -p /opt/foc-demo/bin /evidence /runtime-libs \
 && g++ -std=c++20 -O2 -Wall -Wextra -Werror -fstack-protector-strong -D_FORTIFY_SOURCE=2 -Wl,-z,relro,-z,now /build/supervisor.cpp -o /opt/foc-demo/bin/supervisor \
 && g++ -std=c++20 -O2 -Wall -Wextra -Werror -fstack-protector-strong -D_FORTIFY_SOURCE=2 -Wl,-z,relro,-z,now /build/synthetic_probe.cpp -o /opt/foc-demo/bin/foc-synthetic-probe \
 && g++ --version > /evidence/compiler.txt && dpkg-query -W > /evidence/dependencies.txt \
 && cp -L /usr/lib/x86_64-linux-gnu/libstdc++.so.6 /runtime-libs/libstdc++.so.6
FROM --platform=linux/amd64 python:3.13.13-slim-bookworm@sha256:355bfa66770995d7e9a0da4b3473b44d0cb451f6b56f5615ad9c39e3c4eca03f
COPY --from=build /opt/foc-demo/bin /opt/foc-demo/bin
COPY --from=build /evidence /evidence
COPY --from=build /runtime-libs /usr/local/lib
RUN --network=none ldconfig
USER 10001:10001
ENTRYPOINT ["/opt/foc-demo/bin/supervisor"]
