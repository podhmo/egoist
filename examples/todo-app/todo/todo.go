package todo

import "time"

var (
	Data = []Todo{}
	Now  = time.Now
)

type Todo struct {
	Content   string
	CreatedAt time.Time
}

func Add(content string) {
	Data = append(Data, Todo{
		Content:   content,
		CreatedAt: Now(),
	})
}

func List() []Todo {
	return Data
}
