import React from "react"
import { Route, Switch } from "react-router-dom"
import { SettingsContext } from "../../Context"
import { RouteErrorBoundary, RouteNotFound } from "../../UI"
import * as urls from "../../urls"
import AllThreadsList from "./AllThreadsList"
import { MobileCategoryNavModal } from "./MobileCategoryNav"
import CategoryThreadsList from "./CategoryThreadsList"
import { IActiveCategory } from "./Threads.types"

interface ICategoriesModalState {
  isOpen: boolean
  active?: IActiveCategory | null
}

const Threads: React.FC = () => {
  const settings = React.useContext(SettingsContext)
  const [{ active, isOpen }, setState] = React.useState<ICategoriesModalState>(
    {
      active: null,
      isOpen: false,
    }
  )
  const open = (active?: IActiveCategory | null) => {
    setState({ isOpen: true, active: active || null })
  }
  const close = () => setState({ isOpen: false, active: null })

  return (
    <>
      <MobileCategoryNavModal active={active} close={close} isOpen={isOpen} />
      <Switch>
        <Route
          path={urls.category({ id: ":id", slug: ":slug" })}
          render={() => (
            <RouteErrorBoundary>
              <CategoryThreadsList openCategoryPicker={open} />
            </RouteErrorBoundary>
          )}
          exact
        />
        <Route
          path={settings?.forumIndexThreads ? urls.index() : urls.threads()}
          render={() => (
            <RouteErrorBoundary>
              <AllThreadsList openCategoryPicker={open} />
            </RouteErrorBoundary>
          )}
          exact
        />
        <Route path={urls.index()} component={RouteNotFound} />
      </Switch>
    </>
  )
}

export default Threads