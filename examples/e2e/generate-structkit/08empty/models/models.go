package models

import (
	"github.com/podhmo/maperr"
	"encoding/json"
)

// this file is generated by egoist.generators.structkit

type Person struct {
	Name string `json:"name"`
	Age int `json:"age"`
	Empty Empty `json:"empty"`
}

func (p *Person) UnmarshalJSON(b []byte) error {
	var err *maperr.Error

	// loading internal data
	var inner struct {
		Name *string `json:"name"`// required
		Age *int `json:"age"`// required
		Empty *json.RawMessage `json:"empty"`// required
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
		if inner.Empty != nil  {
			if rawerr := json.Unmarshal(*inner.Empty, &p.Empty); rawerr != nil  {
				err = err.Add("empty", maperr.Message{Error: rawerr})
			}
		} else  {
			err = err.Add("empty", maperr.Message{Text: "required"})
		}
	}

	return err.Untyped()
}

type Empty struct {

}