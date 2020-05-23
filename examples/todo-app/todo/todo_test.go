package todo

import (
	"reflect"
	"testing"
	"time"
)

func TestIt(t *testing.T) {
	now, err := time.Parse(time.RFC3339, "2020-01-01T00:00:00Z")
	if err != nil {
		t.Fatal(err)
	}
	s := TodoStore{
		Now: func() time.Time { return now },
	}

	var empty []Todo
	if !reflect.DeepEqual(s.List(), empty) {
		t.Fatalf("want nil, but %+#v", s.List())
	}

	s.Add("hello")
	s.Add("byebye")

	want := []Todo{
		{Content: "hello", CreatedAt: s.Now()},
		{Content: "byebye", CreatedAt: s.Now()},
	}
	if !reflect.DeepEqual(s.List(), want) {
		t.Fatalf("want\n\t%+#v,\nbut\n\t%+#v", want, s.List())
	}

}
