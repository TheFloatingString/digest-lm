"use client"

import { AppSidebar } from "@/components/app-sidebar"

import { AlertCircleIcon, BadgeCheckIcon, CheckIcon } from "lucide-react"
import { Badge } from "@/components/ui/badge"

import { ChartAreaInteractive } from "@/components/chart-area-interactive"
import { DataTable } from "@/components/data-table"
import { SectionCards } from "@/components/section-cards"
import { SiteHeader } from "@/components/site-header"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"

import data from "./data.json"
import { Card, CardTitle, CardDescription, CardHeader, CardContent } from "@/components/ui/card"
import { useEffect, useRef, useState } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"


import { Bar, BarChart, CartesianGrid, XAxis } from "recharts"
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"

const chartConfig = {
  HTTP_2xx: {
    label: "HTTP_2xx",
    color: "#2563eb",
  },
  HTTP_error: {
    label: "HTTP_error",
    color: "#60a5fa",
  },
} satisfies ChartConfig

export default function Page() {

  function userMessage(message: string) {
    return (
      <div className="self-end bg-blue-500 text-white rounded-xl p-2 max-w-xs w-64 m-4 ml-auto">
        {message}
      </div>
    )
  }

  function assistantMessage(message: string) {
    return (
      <div className="self-start bg-gray-200 dark:bg-gray-700 rounded-xl p-2 max-w-xs w-64 m-4">
        {message}
      </div>
    )
  }

  function outputMessage(name: string, status_code: string) {
    return (
      <Card className="p-2 m-2">
        <Badge variant="secondary">{status_code}</Badge>
        {name}
      </Card>
    )
  }

  const [chartData, setChartData] = useState([
    { timestamp: "January", HTTP_2xx: 186, HTTP_error: 80 },
    { timestamp: "February", HTTP_2xx: 305, HTTP_error: 200 },
    { timestamp: "March", HTTP_2xx: 237, HTTP_error: 120 },
    { timestamp: "April", HTTP_2xx: 73, HTTP_error: 190 },
    { timestamp: "May", HTTP_2xx: 209, HTTP_error: 130 },
    { timestamp: "June", HTTP_2xx: 214, HTTP_error: 140 },
  ]);


  const [messages, setMessages] = useState([

  ])

  const [actions, setActions] = useState([


  ])

  const [requestsPerMinute, setRequestsPerMinute] = useState([


  ])

  const [unitTests, setUnitTests] = useState([

  ])

  const [output, setOutput] = useState([


  ])

  const [successRate, setSuccessRate] = useState(0)

  const [message, setMessage] = useState("")

  const bottomRef = useRef(null);



  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    fetch("http://localhost:6020/digest-lm/unit-tests")
      .then(response => response.json())
      .then(data => {

        setUnitTests(prev => [...prev, ...data.tests]);

        // setUnitTests(data.tests)
      })
      .catch(error => console.error("Error:", error));
    fetch("http://localhost:6020/digest-lm/requests-per-minute")
      .then(response => response.json())
      .then(data => {
        // setRequestsPerMinute(prev => [...prev, ...data.requests]);
        setChartData(data.requests);

      })
      .catch(error => console.error("Error:", error));
    fetch("http://localhost:6020/digest-lm/output")
      .then(response => response.json())
      .then(data => {
        setOutput(prev => [...prev, ...data.output]);
      })
      .catch(error => console.error("Error:", error));
    fetch("http://localhost:6020/digest-lm/actions")
      .then(response => response.json())
      .then(data => {
        setActions(prev => [...prev, ...data.actions]);
      })
      .catch(error => console.error("Error:", error));
    fetch("http://localhost:6020/digest-lm/success-rate")
      .then(response => response.json())
      .then(data => {
        setSuccessRate(data.success_rate);
      })
      .catch(error => console.error("Error:", error));
  }, [messages]); // scrolls every time messages update

  return (
    <SidebarProvider
      style={
        {
          "--sidebar-width": "calc(var(--spacing) * 72)",
          "--header-height": "calc(var(--spacing) * 12)",
        } as React.CSSProperties
      }
    >
      <AppSidebar variant="inset" />
      <SidebarInset>
        <SiteHeader />
        <div className="flex flex-1 flex-col">
          <div className="@container/main flex flex-1 flex-col gap-2">
            {/* <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6"> */}
            <div className="grid grid-cols-3 gap-4 p-4 lg:px-6">
              <Card className="row-span-1 col-span-1 flex flex-col">
                <CardHeader>
                  <CardTitle>Chat</CardTitle>
                  <CardDescription>User conversation</CardDescription>
                </CardHeader>

                <div className="flex-1 overflow-y-auto px-4 space-y-2">
                  {/* Chat messages */}
                  <div className="flex flex-col space-y-2">
                    <ScrollArea className="h-[250px]">
                      {messages.map((message, index) => {
                        return (
                          <div key={index}>{message}</div>
                        )
                      })}
                      <div ref={bottomRef} />
                    </ScrollArea>
                  </div>
                </div>

                {/* Input area */}
                <div className="border-t px-4 py-2">
                  {/* <form className="flex items-center gap-2"> */}
                  <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type your message..."
                    className="flex-1 border rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 m-4 w-70"
                  />
                  <button
                    type="submit"
                    className="bg-blue-500 text-white px-4 py-2 rounded-xl hover:bg-blue-600 text-sm"
                    onClick={() => {
                      setMessages(prev => [...prev, userMessage(message)]);


                      fetch("http://localhost:6020/digest-lm/user-message", {
                        method: "POST",
                        body: JSON.stringify({ message: message })
                      })
                        .then(response => response.json())
                        .then(data => {
                          console.log(data.message)
                          console.log(data)

                          setMessages(prev => [...prev, assistantMessage(data.message)]);

                          console.log(messages)
                        })
                        .catch(error => console.error("Error:", error));
                    }}
                  >
                    Send
                  </button>
                  {/* </form> */}
                </div>
              </Card>



              <Card className="row-span-1 col-span-1">
                <CardHeader>
                  <CardTitle>Actions</CardTitle>
                  <CardDescription>digest-lm steps</CardDescription>
                </CardHeader>
                <CardContent>
                  <ScrollArea>
                    {actions.map((action, index) => (
                      <div key={index}>{action.name}</div>
                    ))}
                  </ScrollArea>
                </CardContent>
              </Card>

              <Card className="row-span-1 col-span-1">
                <CardHeader>
                  <CardTitle>Test Success Rate</CardTitle>
                  <CardDescription><p className="text-2xl font-semibold tabular-nums">{successRate} %</p></CardDescription>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[250px]">
                    {requestsPerMinute.map((request, index) => (
                      <div key={index}>{request.name}</div>
                    ))}
                  </ScrollArea>
                </CardContent>
              </Card>

              <Card className="row-span-1 col-span-1">
                <CardHeader>
                  <CardTitle>Requests per Minute</CardTitle>
                  <CardDescription>
                  <ChartContainer config={chartConfig} className="min-h-[200px] w-full">
      <BarChart accessibilityLayer data={chartData}>
        <CartesianGrid vertical={false} />
        <XAxis
          dataKey="timestamp"
          tickLine={false}
          tickMargin={10}
          axisLine={false}
          tickFormatter={(value) => value.slice(0, 3)}
        />
        <ChartTooltip content={<ChartTooltipContent />} />
        <Bar dataKey="HTTP_2xx" fill="var(--color-HTTP_2xx)" radius={4} />
        <Bar dataKey="HTTP_error" fill="var(--color-HTTP_error)" radius={4} />
      </BarChart>
    </ChartContainer>

                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[250px]">
                    {requestsPerMinute.map((request, index) => (
                      <div key={index}>{request.name}</div>
                    ))}
                  </ScrollArea>
                </CardContent>
              </Card>

              <Card className="row-span-1 col-span-1">
                <CardHeader>
                  <CardTitle>Unit Tests</CardTitle>
                  <CardDescription>curl Requests</CardDescription>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[250px]">
                    {unitTests.map((test, index) => (
                      <div key={index}>{test.name}</div>
                    ))}
                  </ScrollArea>
                </CardContent>
              </Card>

              <Card className="row-span-1 col-span-1">
                <CardHeader>
                  <CardTitle>Output</CardTitle>
                  <CardDescription>HTTP Responses</CardDescription>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[250px]">
                    {output.map((output, index) => (
                      <div key={index}>{outputMessage(output.name, output.description)}</div>
                    ))}
                  </ScrollArea>
                </CardContent>
              </Card>

              {/* <SectionCards /> */}
              {/* <div className="px-4 lg:px-6">
                <ChartAreaInteractive />
              </div> */}
              {/* <DataTable data={data} /> */}

            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
