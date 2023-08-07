import Image from 'next/image'
import Link from 'next/link'
import { Button } from "@/components/ui/button"
import Navbar from './Navbar/page'
import Banner from './Banner/page'

export default function Home() {
  
  return (
   <>
      <div>
<Navbar/>
<Banner/>
    </div>
   </>
  )
}
