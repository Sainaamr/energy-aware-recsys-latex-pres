FILE := main
OUT  := build

.PHONY: pdf
pdf:
	latexmk -pdf -interaction=nonstopmode -outdir=$(OUT) -synctex=1 -halt-on-error $(FILE)

.PHONY: watch
watch:
	latexmk -pdf -interaction=nonstopmode -outdir=$(OUT) -synctex=1 -pvc -view=none -halt-on-error $(FILE)

.PHONY: clean
clean:
	rm -rf $(filter-out $(OUT)/$(FILE).pdf, $(wildcard $(OUT)/*))
