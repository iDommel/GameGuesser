import React, {useState, useEffect} from 'react'
import logo from './pizza.jpeg';
import './App.css';
import { Select, Card, Space } from 'antd';
import { define } from 'mime';

import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Grid from '@mui/material/Unstable_Grid2';
import CachedIcon from '@mui/icons-material/Cached';
import IconButton from '@mui/material/IconButton';
import { error } from 'console';

const { Option } = Select;

interface gameTypeDb {
  appId: number,
  categories: string[],
  developers: string[],
  tags: string[],
  name: string,
  publishers: string[],
  release: string | number,
  price: string,
  requiredAge: number,
  score: number | null,
  image: string
}

interface gameType extends gameTypeDb {
  label: string,
  value: string,
  key: number,
}

enum answerNumber{
  inferior,
  superior,
  equal,
}

interface answerArrayType {
  answer: boolean
  data: string
}

interface answerNumberType {
  answer : answerNumber
  data: number
}

type gameTypeAnswer = {
  appId: number,
  categories: answerArrayType[],
  developers: answerArrayType[],
  tags: answerArrayType[],
  name: string,
  publishers: answerArrayType[],
  release: string | number,
  price: string,
  requiredAge: answerNumberType,
  score: number | null,
  isWin: boolean
  image: string
}

type FillCardLabelsProps = {
  label: answerArrayType[];
  labelName: string;
  isWin: boolean;
};

type FillCardNumbersProps = {
  label: answerNumberType;
  labelName: string;
  isWin: boolean;
};
const compArray = (data: string[], compData: string[], label: string): answerArrayType[] => {
  let answer: answerArrayType[] = []

  if (data === undefined){
    console.log("data undefined ", label)
    return []
  } else if (compData === undefined) {
    console.log("compData undefined")
    return []
  }
  data.forEach(element => {
    if (compData.includes(element)) {
      answer.push({answer: true, data: element})
    } else {
      answer.push({answer: false, data: element})
    }
  });

  return answer
}

const compGamesNumbers = (data: number, compNumber: number): answerNumberType => {
  let answer: answerNumberType = {answer: answerNumber.equal, data: data}
  if (data < compNumber) {
    answer.answer = 0
  } else if (data > compNumber) {
    answer.answer = 1
  }
  return answer
}

function App() {

  const [searchGame, setSearchGame] = useState("")
  const [selectedGames, setSelectedGames] = useState<gameTypeAnswer[] | undefined>(undefined)
  const [gameToguess, setGameToGuess] = useState<gameType | undefined>(undefined)
  const [gamesData, setGamesData] = useState<gameType[]>([])

  const getGames = async () => {
    const dbData = await fetch('http://localhost:8000/games')
    const gamesJson = await dbData.json()
    const formattedData: gameType[]= []
    for (let index = 0; index < gamesJson.length; index++) {
      const id = gamesJson[index].appId as number
      const data: gameType = {
        appId: gamesJson[index].appId,
        categories: gamesJson[index].categories,
        developers: gamesJson[index].developers,
        tags: gamesJson[index].tags as string[],
        name: gamesJson[index].name,
        publishers: gamesJson[index].publishers,
        release: gamesJson[index].release,
        price: gamesJson[index].price,
        requiredAge: gamesJson[index].requiredAge,
        score: gamesJson[index].score,
        label: gamesJson[index].name,
        value: gamesJson[index].name,
        image: gamesJson[index].image,
        key: index,
      }
      formattedData.push(data)
    }
    console.log("formatted data : ", formattedData)
    setGamesData(formattedData)
  }

  const getGameToGuess = async () => {
    const dbData = await fetch('http://localhost:8000/get_current_game')
    const gameJson = await dbData.json()
    console.log("game to guess : ", gameJson)
    setGameToGuess(gameJson)
  }

  const randomizeAndGetNewGame = async () => {
    await fetch('http://localhost:8000/randomize_current_game').then(
      response => response.json()
    ).then(data => {
      console.log(data)
      getGameToGuess()
    }
    ).catch(error => console.log(error))
  }

  useEffect(() => {
    getGames()
    getGameToGuess()
  }, [])

  const compGames = (searchGame: gameType) => {
    console.log("searchGame : ", searchGame.categories)
    if (gameToguess != undefined && searchGame.name.toLowerCase() === gameToguess.name.toLowerCase()) {
      console.log("win")
      const answerData: gameTypeAnswer = {
        appId: searchGame.appId,
        categories: compArray(searchGame.categories, gameToguess.categories, "categories"),
        developers: compArray(searchGame.developers, gameToguess.developers, "devs"),
        tags: compArray(searchGame.tags, gameToguess.tags, "tags"),
        name: searchGame.name,
        publishers: compArray(searchGame.publishers, gameToguess.publishers, "publishers"),
        release: searchGame.release,
        price: searchGame.price,
        requiredAge: compGamesNumbers(Number(searchGame.release), Number(gameToguess.release)),
        score: searchGame.score,
        image : searchGame.image,
        isWin: true
      }
      return answerData
    } else if (gameToguess != undefined) {
      const answerData: gameTypeAnswer = {
        appId: searchGame.appId,
        categories: compArray(searchGame.categories, gameToguess.categories, "categories"),
        developers: compArray(searchGame.developers, gameToguess.developers, "devs"),
        tags: compArray(searchGame.tags, gameToguess.tags, "tags"),
        name: searchGame.name,
        publishers: compArray(searchGame.publishers, gameToguess.publishers, "publishers"),
        release: searchGame.release,
        price: searchGame.price,
        requiredAge: compGamesNumbers(Number(searchGame.release), Number(gameToguess.release)),
        score: searchGame.score,
        image : searchGame.image,
        isWin: false
      }
      console.log("answerData : ", answerData)
      return answerData
    }
  }

  const onChange = (value: string, option: gameType | gameType[]) => {
    console.log(`selected ${value}  key = ${(option as gameType).key} release : ${(option as gameType).price}`);
    console.log("searchGame : ", (option as gameType).appId)
    const gameAnswer = compGames(option as gameType)

    if (selectedGames == undefined) {
      if (gameAnswer != undefined) {
        setSelectedGames([gameAnswer]);
      }
    } else {
      if (gameAnswer != undefined) {
        setSelectedGames([...selectedGames, gameAnswer]);
      }

    }
  };

  const onSearch = (label: string) => {
    console.log('search:', label);
    setSearchGame(label)
  };

  // Filter `option.label` match the user type `input`
  const filterOption = (input: string, option?: { label: string; value: any }) =>
    (option?.label ?? '').toLowerCase().includes(input.toLowerCase());

  const FillCardLabels = ({label, labelName, isWin}: FillCardLabelsProps) => {
    return (
      <Card title={labelName} bordered={false} style={isWin ? {backgroundColor:"green", flexDirection:"row"} : {backgroundColor:"white", flexDirection:"row"}}>
        {label.map((item, index) => (
          <p style={item.answer ? {backgroundColor:"green", margin: 5} : {backgroundColor:"red", margin: 5}} key={index}>{item.data}</p>
        ))}
      </Card>
    )
  }

  const FillCardNumbers = ({label, labelName, isWin}: FillCardNumbersProps) => {
    return (
      <Card title={labelName} style={{flexDirection:"row"}}>
        <p style={label.answer === answerNumber.equal ? {backgroundColor:"green", margin: 5} : {backgroundColor:"red", margin: 5}}>{label.data.toString()}</p>
      </Card>
    )
  }

  return (
    <div className="App">
      <AppBar position="static" >
        <Toolbar variant="dense" style={{alignContent:"center", justifyContent:"center"}}>
        <Select
          showSearch
          placeholder="Select a person"
          optionFilterProp="children"
          onChange={onChange}
          onSearch={onSearch}
          filterOption={filterOption}
         // options={gamesData}
        //  optionLabelProp="label"
          style={{width:"300px"}}
        >
          {gamesData.map((element:gameType, index: number) => (
                <Option 
                  value={element.value}
                  label={element.label}
                  requiredAge={element.requiredAge}
                  price={element.price}
                  release={element.release}
                  publishers={element.publishers}
                  name={element.name}
                  tags={element.tags}
                  developers={element.developers}
                  categories={element.categories} 
                  appId={element.appId}
                >
                  <Space>
                    <span role="img" aria-label={element.label}>
                      <img src={element.image} width="60px" height="30px" style={{marginTop:10}}/>
                    </span>
                    {element.name}
                  </Space>
              </Option>
          ))}
        </Select>
        <IconButton
            onClick={randomizeAndGetNewGame}
            size="large"
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 2 }}
            style={{marginLeft:10}}
          >
            <CachedIcon/>
          </IconButton>
        <div style={{flexDirection:"row"}}>
        </div>
        </Toolbar>
      </AppBar>
      <header className="App-header">
        <div style={{flexDirection:"column"}}>
          {selectedGames === undefined ? <p>try to guess the game</p> : selectedGames.slice(0).reverse().map((game: gameTypeAnswer, index:number) => (
            <Card title={game.name} bordered={true} style={game.isWin ? styles.winCard : styles.loseCard} key={index}>
              <img src={game.image}/>

              <FillCardLabels label={game.categories} labelName={"categories"} isWin={game.isWin}/>
              <FillCardLabels label={game.developers} labelName={"developers"} isWin={game.isWin}/>
              <FillCardLabels label={game.publishers} labelName={"publishers"} isWin={game.isWin}/>
            </Card>
          ))}
        </div>
      </header>
    </div>
  );
}

const styles = {
  loseCard: {
    width: 800,
    margin: 40,
    borderColor: "red",
    borderWidth:2
  },
  winCard: {
    width: 800,
    margin: 40,
    borderColor: "green",
    borderWidth:2,
    backgroundColor: "green"
  }
}
export default App;

