# kbal build. Needs HiGHS (brew install highs); build without it with: make NOHIGHS=1
HIGHS_PREFIX ?= /opt/homebrew
CXX ?= clang++
CXXFLAGS ?= -std=c++17 -O3 -march=native -DNDEBUG -Wall -Wno-unused-function
ifdef NOHIGHS
CXXFLAGS += -DKBAL_NO_HIGHS
LDFLAGS ?=
else
CXXFLAGS += -I$(HIGHS_PREFIX)/include/highs
LDFLAGS ?= -L$(HIGHS_PREFIX)/lib -lhighs -Wl,-rpath,$(HIGHS_PREFIX)/lib
endif

kbal: kbal.cpp
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS) -lpthread

clean:
	rm -f kbal
