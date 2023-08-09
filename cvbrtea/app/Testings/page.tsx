'use client'
import { useEffect, useState } from 'react';

interface Item {
  title: string; // You can adjust this type based on your actual data structure
  // Add other properties as needed
}

function Testings() {
  const [data, setData] = useState<Item[]>([]);

  useEffect(() => {
    async function fetchData() {
      const res = await fetch('/api/python');
      const json: Item[] = await res.json(); // Explicitly set the type here
      setData(json);
    }
    fetchData();
  }, []);

  return (
    <ul>
      {data.map((item, index) => (
        <li key={index}>{item.title}</li>
      ))}
    </ul>
  );
}

export default Testings;
