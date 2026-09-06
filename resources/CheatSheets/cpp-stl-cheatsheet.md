---
title: C++ STL 速查表
description: 此处实现了部分 STL 库内容。
created: 2022-10-22
---

<a id="table-of-contents"></a>
## 目录

- [面向开发者的 C++ STL 速查表](#cpp-stl-cheatsheet-for-developers)
	- [Vector](#vector)
		- [Vector 插入](#vector)
		- [Vector 显示](#vector)
		- [Vector 最大元素](#vector)
		- [Vector 最小元素](#vector)
		- [Vector 排序](#vector)
		- [Vector 反转](#vector)
		- [Vector 删除](#vector)
	- [Set](#set)
		- [Set 插入](#set)
		- [Set 显示](#set)
	- [无序集合](#unordered-set)
		- [无序集合插入](#unordered-set)
		- [无序集合显示](#unordered-set)
	- [Map](#map)
		- [Map 插入](#map)
		- [Map 显示](#map)
	- [栈](#stack)
		- [栈插入](#stack)
		- [栈显示](#stack)
	- [队列](#queue)
		- [队列插入](#queue)
		- [队列显示](#queue)
	- [双端队列](#deque)
		- [双端队列插入](#deque)
		- [双端队列显示](#deque)
    - [向量对](#vector-pair)
		- [向量对插入](#vector-pair)
		- [向量对显示](#vector-pair)
	- [列表](#list)
		- [列表插入](#list)
		- [列表显示](#list)
		- [列表删除](#list)
	- [优先队列](#priority-queue)
		- [优先队列插入](#priority-queue)
		- [优先队列显示](#priority-queue)

<a id="cpp-stl-cheatsheet-for-developers"></a>
# C++ STL CheatSheet for Developers

<a id="vector"></a>
## Vector

```cpp 
    // Vector  initialization 
    vector <int> v;
    
    // Vector  Insertion element
    cout << "Insertion of element in vector: " << endl;
    cout << endl;

    for (int i = 0; i < n; i++)
    {
        v.push_back(a[i]);
    }
    
    // Vector  Display element
    cout << "Display element of vector " << endl;

    for (int i = 0; i < n; i++)
    {
        cout << v[i] << " ";
    }
    cout << endl;
    
    // Vector maximum element
    int maximum = *max_element(v.begin(), v.end());
    
    // Vector minimum element
    int minimum = *min_element(v.begin(), v.end());

    cout << "Maximum element in vector " << maximum << endl;
    cout << "Minimum element in vector " << minimum << endl;
    sort(v.begin(), v.end());

    // Vector sort element
    cout << "Sort element of vector " << endl;
    for (int i = 0; i < n; i++)
    {
        cout << v[i] << " ";
    }
    reverse(v.begin(), v.end());
    cout << endl;

    // Vector reverse element
    cout << "Reverse element of vector " << minimum << endl;
    for (int i = 0; i < n; i++)
    {
        cout << v[i] << " ";
    }
    cout << endl;

    // Vector deletion
    cout << "Delete last element of vector " << endl;
    v.pop_back();
    for (int i = 0; i < n; i++)
    {
        cout << v[i] << " ";
    }
```

**[🔼Back to Top](#table-of-contents)**

<a id="set"></a>
## Set

```cpp
    // Set initialization 
    set <int> s;
    cout << endl;

    // Set insertion 
    cout << "Insertion in set " << endl;
    cout << endl;

    for (int i = 0; i < n; i++)
    {
        s.insert(a[i]);
    }

    // Set display
    cout << "Display of set element" << endl;

    for (auto i = s.begin(); i != s.end(); i++)
    {
        cout << *i << " ";
    }
```

**[🔼Back to Top](#table-of-contents)**

<a id="unordered-set"></a>
## Unordered-Set

```cpp
    // Unordered Set initialization 
    unordered_set <int> s1;
    cout << endl;
    
    // Unordered set insertion 
    cout << "Insertion in unordered set " << endl;

    for (int i = 0; i < n; i++)
    {
        s1.insert(a[i]);
    }
    
    // Unordered set display
    cout << "Display of unordered set element" << endl;

    for (auto i = s1.begin(); i != s1.end(); i++)
    {
        cout << *i << " ";
    }
```

**[🔼Back to Top](#table-of-contents)**

<a id="map"></a>
## Map

```cpp
    // Map initialization 
    map <int, int> m;
    cout << endl;
    
    // Map insertion
    cout << "Insertion in map " << endl;
    for (int i = 0; i < n; i++)
    {
        m[a[i]]++;
    }
    cout << "Display of map element" << endl;
    
    // Map display
    for (auto i = m.begin(); i != m.end(); i++)
    {
        cout << i->first << " " << i->second << endl;
    }  
```

**[🔼Back to Top](#table-of-contents)**

<a id="stack"></a>
## Stack 

```cpp
    // Stack initialization 
    stack<int> st;
    cout << endl;

    // Stack insertion
    cout << "Insertion in stack " << endl;

    for (int i = 0; i < n; i++)
    {
        st.push(a[i]);
    }
    
    // Stack display
    cout << "Display and removal of stack element" << endl;

    for (auto i = s.begin(); i != s.end(); i++)
    {
        cout << st.top() << " ";
        st.pop();
    } 
```

**[🔼Back to Top](#table-of-contents)**

<a id="queue"></a>
## Queue

```cpp
    // Queue initialization 
	queue<int> q;
    cout << endl;

    // Queue insertion
    cout << "Insertion in queue " << endl;

    for (int i = 0; i < n; i++)
    {
        q.push(a[i]);
    }
    
    // Queue display
    cout << "Display of queue element" << endl;

    for (auto i = s.begin(); i != s.end(); i++)
    {
        cout << q.front() << " ";
        q.pop();
    }
```

**[🔼Back to Top](#table-of-contents)**

<a id="deque"></a>
## Deque

```cpp
    // Deque initialization 
    deque <int> d;

    // Deque insertion
    cout << "Insertion in deqeue " << endl;

    for (int i = 0; i < n; i++)
    {
        d.push_front(a[i]);
    }
    cout << "Display of dequeue element" << endl;

    // Deque display
    for (auto i = s.begin(); i != s.end(); i++)
    {
        cout << d.front() << " ";
        d.pop_back();
    }
    cout << "Deletion of dequeue element" << endl;

    d.pop_back(); 
```

**[🔼Back to Top](#table-of-contents)**

<a id="vector-pair"></a>
## Vector-Pair

```cpp
    // Vector pair initialization 
    vector<pair<int, int>> p;
    
    // Vector pair insertion
    cout << "Insertion in vector pair " << endl;
    cout << endl;

    for (int i = 0; i < n; i++)
    {
        p.push_back({a[i], i});
    }

    // Vector pair display
    cout << "Display of vector pair element" << endl;

    for (auto i = 0; i < v.size(); i++)
    {
        cout << p[i].first << " " << p[i].second << endl;
    }
    cout << endl;
    
    // Vector pair sorting according to first element
    cout << "Sorting according to first element\n";
    sort (v.begin(), v.end());
    cout << "\n";
    
    // Vector pair sorting according to second element
    cout << "Sorting according to second element\n";
    bool second_sorter (const pair <int,int> &a, const pair <int,int> &b) // comparator function, to be put outside main
    {
    	return (a.second < b.second);
    }
    sort (v.begin(), v.end(), second_sorter);
    cout << "\n";
```

**[🔼Back to Top](#table-of-contents)**

<a id="list"></a>
## List

```cpp
    // List initialization 
    list <int> LI;
    list <int>::iterator it;
    
    // Inserts elements at end of list
    LI.push_back(4);

    // Inserts elements at beginning of list
    LI.push_front(3);

    // Returns reference to first element of list
    it = LI.begin();

    // Inserts 1 before first element of list
    LI.insert(it,1);

    // List traversal
    for(it = LI.begin();it!=LI.end();it++)
    {
        cout<<*it<<" ";
    }
    cout<<endl;

    // Reverse elements of list
    LI.reverse();

    // Removes all occurrences of 5 from list
    LI.remove(5);

    // Removes last element from list
    LI.pop_back();
	
    // Removes first element from list
    LI.pop_front();
```

**[🔼Back to Top](#table-of-contents)**

<a id="priority-queue"></a>
## Priority Queue

```cpp
    // Priority Queue initialization 
	priority_queue<int> pq;

	// Priority queue insertion
	pq.push(10);
	pq.push(20);

	// Priority queue display
	while (!pq.empty()) {
		cout << '\t' << g.top();
		g.pop();
	}
	cout << '\n';
	
	cout << "\n size if pq : " << pq.size();
	cout << "\n top element of pq : " << pq.top();
	
	// Priority queue deletion
	pq.pop();
```

**[🔼Back to Top](#table-of-contents)**
