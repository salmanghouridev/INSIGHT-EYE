import Image from 'next/image'
import Link from 'next/link'
import { Button } from "@/components/ui/button"
import Navbar from './Navbar/page'
import Banner from './Banner/page'
import React, { useState, useEffect } from 'react';
import Header from '@/components/Header'
import { RootState } from './GlobalRedux/store'
import { useSelector, useDispatch } from 'react-redux'
import { increment, decrement,incrementByAmount} from '@/app/GlobalRedux/Features/counter/counterSlice'

export default function Home() {

  return (
   <>
      <div>
<Header/>
<Navbar/>
<Banner/>

    </div>
   </>
  )
}
