## motivation

- コード生成はIaC (Infrastructure as Code) におけるデプロイのようなもの
- メタプログラミングをpreprocessのタイミングで行い実行時には行わない
- アプリケーションコードとはランタイムのこと

## お気持ち

- YAMLは補完が効かないし、モジュールシステムも無い
- main.goは生成するもの
- yoman, cookiecutterと衝突しない
- scaffoldは onetime deploy 、やりたいのは continuous deploy

## 記事

- [goはランタイムという発想のミニフレームワークを作り始めた](https://pod.hatenablog.com/entry/2020/04/30/224205)
- [hello worldについての詳しい解説](https://pod.hatenablog.com/entry/2020/05/13/183014)
