package todo

import (
	"m/store"
	"time"
)

type TodoStore struct {
	Filename string
	Data     []Todo
	Now      func() time.Time
}

func (s *TodoStore) Add(content string) {
	s.Data = append(s.Data, Todo{
		Content:   content,
		CreatedAt: s.Now(),
	})
}

func (s *TodoStore) List() []Todo {
	return s.Data
}

func (s *TodoStore) Load() error {
	return store.Load(s.Filename, &s.Data)
}

func (s *TodoStore) Save() error {
	return store.Save(s.Filename, &s.Data)
}
