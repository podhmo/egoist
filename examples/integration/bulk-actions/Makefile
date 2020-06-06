default: 00 01 02 03 04

# parse normal
00:
	python parse.py foo bar boo | tee $@.parsed.output

# parse with flags
01:
	python parse.py foo --bar boo -n 1 -v --level=info | tee $@.parsed.output

# parse with separator ('-')
02:
	python parse.py x - y - z | tee $@.parsed.output

# parse end of arguments is separator ('-')
03:
	python parse.py x - y - z - | tee $@.parsed.output

# complex example
04:
	python parse.py \
 first foo --bar - \
 second boo -n 1  - \
 third -v --level=info \
 | tee $@.parsed.output


