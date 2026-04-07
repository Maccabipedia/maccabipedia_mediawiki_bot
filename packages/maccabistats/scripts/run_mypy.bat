pushd %~dp0..\src

mypy -p maccabistats

popd
pause