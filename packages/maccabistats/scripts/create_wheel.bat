pushd %~dp0..\

python setup.py bdist_wheel --dist-dir=wheels

popd
pause