import React, {useState} from 'react'
import logo from './pizza.jpeg';
import './App.css';
import { Select } from 'antd';

function App() {
  const countries = [
    { label: "Belgium", value: "Europe", key: 0 },
    { label: "India", value: "Asia", key: 1 },
    { label: "Bolivia", value: "South America", key: 2 },
    { label: "Ghana", value: "Africa", key: 3},
    { label: "Japan", value: "Asia", key: 4 },
    { label: "Canada", value: "North America", key: 5 },
    { label: "New Zealand", value: "Australasia", key: 6 },
    { label: "Italy", value: "Europe", key: 7 },
    { label: "South Africa", value: "Africa", key: 8 },
    { label: "China", value: "Asia", key: 9 },
    { label: "Paraguay", value: "South America", key: 10 },
    { label: "Usa", value: "North America", key: 11 },
    { label: "France", value: "Europe", key: 12 },
    { label: "Botswana", value: "Africa", key: 13 },
    { label: "Spain", value: "Europe", key: 14},
    { label: "Senegal", value: "Africa", key: 15},
    { label: "Brazil", value: "South America", key: 16},
    { label: "Denmark", value: "Europe", key: 17 },
    { label: "Mexico", value: "South America", key: 18 },
    { label: "Australia", value: "Australasia", key: 19},
    { label: "Tanzania", value: "Africa", key: 20 },
    { label: "Bangladesh", value: "Asia", key: 21 },
    { label: "Portugal", value: "Europe", key: 22 },
    { label: "Pakistan", value: "Asia", key: 23 }
  ];

  const [searchGame, setSearchGame] = useState("")
  const [selectedGames, setSelectedGames] = useState<any[]>([""])
  
  const onChange = (value: string, option: { label: string; value: string; key: number; } | { label: string; value: string; key: number; }[]) => {
    console.log(`selected ${value}  key = ${(option as { label: string; value: string; key: number; }).key}`);
    setSelectedGames([...selectedGames, value]);
  };
  
  const onSearch = (label: string) => {
    console.log('search:', label);
    setSearchGame(label)
  };
  
  // Filter `option.label` match the user type `input`
  const filterOption = (input: string, option?: { label: string; value: any }) =>
    (option?.label ?? '').toLowerCase().includes(input.toLowerCase());
  return (
    <div className="App">
      <header className="App-header">
        <Select
          showSearch
          placeholder="Select a person"
          optionFilterProp="children"
          onChange={onChange}
          onSearch={onSearch}
          filterOption={filterOption}
          options={countries}
        />
        <div style={{flexDirection:"column"}}>
          {selectedGames.map((game, index) => (
            <div>
            <text>{game}</text>
            </div>
          ))}
        </div>
      </header>
    </div>
  );
}

export default App;

