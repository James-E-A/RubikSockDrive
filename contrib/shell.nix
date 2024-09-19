with (import <nixpkgs> {});

mkShell {
  buildInputs = [

    # FIXME: why the heck are modules not importable when I use pypy310 instead of python312??
    (python312.withPackages (python-pkgs: [
      python-pkgs.sympy
      python-pkgs.colorama
      (python-pkgs.buildPythonPackage rec {
        pname = "kociemba";
        version = "1.2.1";

        src = python-pkgs.fetchPypi {
          inherit pname version;
          hash = "sha256-t3Q117DpPpx5Y+SH6Mw4IFQL0cm7n+VmWZnTqN6snuY=";
        };

        pyproject = true;
        dependencies = [
          python-pkgs.cffi
        ];
        build-system = [
          python-pkgs.cffi
          python-pkgs.future
          python-pkgs.pytest-runner
          python-pkgs.setuptools
        ];

      })

    ]))
  ];
}
