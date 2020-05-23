package todo

import (
	"encoding/json"
	"os"
	"time"
)

var (
	Data     = []Todo{}
	Now      = time.Now
	Filename = "todo.json"
)

func Add(content string) {
	Data = append(Data, Todo{
		Content:   content,
		CreatedAt: Now(),
	})
}

func List() []Todo {
	return Data
}

func Load() error {
	f, err := os.Open(Filename)
	if err != nil {
		if os.IsNotExist(err) {
			return Save()
		}
		return err
	}
	defer f.Close()
	decoder := json.NewDecoder(f)
	return decoder.Decode(&Data)
}

func Save() error {
	f, err := os.Create(Filename)
	if err != nil {
		return err
	}
	defer f.Close()
	encoder := json.NewEncoder(f)
	return encoder.Encode(Data)
}
