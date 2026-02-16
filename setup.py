from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.txt").read_text(encoding="utf-8") if (HERE / "README.txt").exists() else ""

setup(
	name="codefox-cli",
	version="0.1.0",
	description="CodeFox CLI — code auditing and scanning tool using Gemini API",
	long_description=README,
	long_description_content_type="text/plain",
	author="",
	packages=find_packages(),
	py_modules=["main"],
	include_package_data=True,
	install_requires=[
		"typer",
		"rich",
		"python-dotenv",
		"GitPython",
		"google-genai",
	],
	entry_points={
		"console_scripts": [
			"codefox=main:main",
		],
	},
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires=">=3.8",
)

