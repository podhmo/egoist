package models

type Person struct {
	Name string `json:"name"`
	Age int `json:"age"`
}

func (p *Person) UnmarshalJSON(b []byte) error {
	import (
		"github.com/podhmo/maperr"
		"encoding/json"
	)

	var err *maperr.Error

	// loading internal data
	var inner struct {
		Name *string `json:"name"`// required
		Age *int `json:"age"`// required
	}
	if rawErr := json.Unmarshal(b, &inner); rawErr != nil  {
		return err.AddSummary(rawErr.Error())
	}

	// binding field value and required check
	{
		if inner.Name != nil  {
			p.Name = *inner.Name
		} else  {
			err = err.Add("name", maperr.Message{Text: "required"})
		}
		if inner.Age != nil  {
			p.Age = *inner.Age
		} else  {
			err = err.Add("age", maperr.Message{Text: "required"})
		}
	}

	return err.Untyped()
}