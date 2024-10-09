{
  description = "Development environment with Python and YDLidar";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    ydlidar-sdk = {
      url = "github:YDLIDAR/YDLidar-SDK";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, flake-utils, ydlidar-sdk }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python311;
        ydlidar = pkgs.stdenv.mkDerivation {
          pname = "ydlidar";
          version = "1.2.4";
          src = ydlidar-sdk;

          nativeBuildInputs = with pkgs; [ cmake swig python ];
          buildInputs = [ python ];
          propagatedBuildInputs = with python.pkgs; [ 
            numpy 
            setuptools
            pip
            wheel
          ];

          cmakeFlags = [
            "-DBUILD_SHARED_LIBS=ON"
            "-DBUILD_PYTHON=ON"
            "-DPYTHON_EXECUTABLE=${python.interpreter}"
            "-DPYTHON_INCLUDE_DIR=${python}/include/python${python.pythonVersion}"
            "-DPYTHON_LIBRARY=${python}/lib/libpython${python.pythonVersion}.so"
          ];

          NIX_CFLAGS_COMPILE = toString [
            "-Wno-format-security"
            "-Wno-format"
            "-Wno-address-of-packed-member"
          ];

          postInstall = ''
            # Ensure the Python module is in the correct location
            mkdir -p $out/${python.sitePackages}
            if [ -f $out/lib/python${python.pythonVersion}/site-packages/ydlidar.py ]; then
              cp -n $out/lib/python${python.pythonVersion}/site-packages/ydlidar.py $out/${python.sitePackages}/
            fi
            if [ -f $out/lib/python${python.pythonVersion}/site-packages/_ydlidar.so ]; then
              cp -n $out/lib/python${python.pythonVersion}/site-packages/_ydlidar.so $out/${python.sitePackages}/
            fi
          '';

          meta = with pkgs.lib; {
            description = "YDLidar SDK for all YDLIDAR products";
            homepage = "https://github.com/YDLIDAR/YDLidar-SDK";
            license = licenses.mit;
            platforms = platforms.unix;
          };
        };
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            (python.withPackages (ps: with ps; [
              matplotlib
            ]))
            ydlidar
          ];

          shellHook = ''
            echo "Python development environment with YDLidar is ready!"
            echo "Python version: $(python --version)"
          '';
        };
      }
    );
}