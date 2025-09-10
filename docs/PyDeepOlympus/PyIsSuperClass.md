## Most Tutorials Call `super()` a Function But It’s Actually a Class

Many tutorials explain **how to use `super()`** and highlight its benefits, but they often use **imprecise terminology**. For example:

* 🔹 [DigitalOcean](https://www.digitalocean.com/community/tutorials/python-super) refers to it as the `super()` function
* 🔹 [GeeksforGeeks](https://www.geeksforgeeks.org/python-super/) also calls it a super() function
* 🔹 [Real Python](https://realpython.com/python-super/) casually uses the same term in its explanations

These descriptions aren't *technically* wrong in terms of simplicity, but they can be **misleading**.


---

##  What Does Python Itself Say?

The **official Python documentation** and the **source code of CPython** treat `super` as a **built-in class**.



`super()` *acts* like a function call, but behind the scenes, you are **instantiating the super class** that returns a **proxy object**

---

##  Proof: `super` is a Class (CPython Source)

Below is the **actual implementation** of `super` in **CPython**, written in C. This makes it crystal clear: `super` is defined as a `PyTypeObject`, which is how Python internally represents classes.

```c
PyTypeObject PySuper_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "super",                                    /* tp_name */
    sizeof(superobject),                        /* tp_basicsize */
    0,                                          /* tp_itemsize */
    /* methods */
    super_dealloc,                              /* tp_dealloc */
    0,                                          /* tp_vectorcall_offset */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_as_async */
    super_repr,                                 /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    super_getattro,                             /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC |
        Py_TPFLAGS_BASETYPE,                    /* tp_flags */
    super_doc,                                  /* tp_doc */
    super_traverse,                             /* tp_traverse */
    0,                                          /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    0,                                          /* tp_iter */
    0,                                          /* tp_iternext */
    0,                                          /* tp_methods */
    super_members,                              /* tp_members */
    0,                                          /* tp_getset */
    0,                                          /* tp_base */
    0,                                          /* tp_dict */
    super_descr_get,                            /* tp_descr_get */
    0,                                          /* tp_descr_set */
    0,                                          /* tp_dictoffset */
    super_init,                                 /* tp_init */
    PyType_GenericAlloc,                        /* tp_alloc */
    PyType_GenericNew,                          /* tp_new */
    PyObject_GC_Del,                            /* tp_free */
    .tp_vectorcall = super_vectorcall,
};
```

---

## Sources I Believe!

*  **CPython Source:** https://github.com/PyDeepOlympus/cPyDeepOlympus/blob/main/Objects/typeobject.c
* **Official Documentation:** https://docs.python.org/3/library/functions.html#super
---
