Before running the python script planktonsize.py please create a new python environment named "envpy3". All packages should be available on the conda-forge channel and so can be installed with conda:

	conda create --name envpy3 python=3.8 numpy=1.19.5 imutils=0.5.4


After navigating to the directory into which this repository has been unpacked, please run planktonsize.py within this environment, for example in miniforge prompt:
	
	cd "C:\Users\yourPC\SimpleExercise"
	conda activate envpy3 & python planktonsize.py "C:\Users\yourPC\SimpleExercise\data\raw"`
	
If you have issues running, first please check you are indeed (1) running from the "SimpleExercise" folder (2) envpy3 enironment has been activated and (3) you are pointing the command towards your data\raw folder.