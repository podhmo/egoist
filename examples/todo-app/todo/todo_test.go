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
	Now = func() time.Time { return now }

	if !reflect.DeepEqual(List(), []Todo{}) {
		t.Fatalf("want nil, but %+#v", List())
	}

	Add("hello")
	Add("byebye")

	want := []Todo{
		{Content: "hello", CreatedAt: Now()},
		{Content: "byebye", CreatedAt: Now()},
	}
	if !reflect.DeepEqual(List(), want) {
		t.Fatalf("want\n\t%+#v,\nbut\n\t%+#v", want, List())
	}

}
