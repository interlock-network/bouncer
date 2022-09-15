{ lib, aiohttp, buildPythonPackage, fetchurl, pytest }:

buildPythonPackage rec {
  pname = "pycord";
  version = "2.1.3";

  src = fetchurl {
    url = "https://files.pythonhosted.org/packages/ed/6a/719898a8baedc7f2abe1eb505f90df881a0339270fdb115283c83b040c7d/py-cord-2.1.3.tar.gz";
    sha256 = "sha256-QWzn9i5dQT6yT/Kq5bDthwGe0uivNVGbrxr/OnqfGCE=";
  };

  doCheck = false;

  propagatedBuildInputs = [
    aiohttp
  ];


  meta = with lib; {
    description = "A fork of discord.py. Pycord is a modern, easy to use, feature-rich, and async ready API wrapper for Discord written in Python.";
    homepage = "https://github.com/Pycord-Development/pycord";
    license = licenses.mit;
    maintainers = with maintainers; [ jmercouris ];
  };

}
