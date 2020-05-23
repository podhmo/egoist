package store

import (
	"encoding/json"
	"os"
)

func Load(filename string, ob interface{}) error {
	f, err := os.Open(filename)
	if err != nil {
		if os.IsNotExist(err) {
			return Save(filename, ob)
		}
		return err
	}
	defer f.Close()
	decoder := json.NewDecoder(f)
	return decoder.Decode(ob)
}

func Save(filename string, ob interface{}) error {
	f, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer f.Close()
	encoder := json.NewEncoder(f)
	return encoder.Encode(ob)
}
