NO_NUMPY = False
try:
    import numpy as np
except ImportError:
    NO_NUMPY = True


PAYBACK_PERIOD = 10  # Days
SHIPBACK_PERIOD = 6  # Days
PURCHASE_PERIOD = 3  # Days
STOCK_REDUNDANCY = 1.1


class DayResult:
    def __init__(self, price, sales, successfulRate, successful, failed, costsPerSale, costsPerStep, stocks, futureStocks, cash, transaction, receivables):
        self.price = price
        self.sales = sales
        self.successfulRate = successfulRate
        self.successful = successful
        self.failed = failed
        self.costsPerSale = costsPerSale
        self.costsPerStep = costsPerStep
        self.stocks = stocks
        self.futureStocks = futureStocks
        self.cash = cash
        self.transaction = transaction
        self.receivables = receivables


class Cost:
    def __init__(self, description, amount):
        self.description = description
        self.amount = amount


class Transaction:
    def __init__(self, direction, amount, quantity, description):
        if (direction is not 'Deposit' and direction is not 'Withdrawal') and (type(amount) is not int and type(amount) is not float) and type(quantity) is not int:
            raise TypeError
        self.direction = direction
        self.amount = round(amount, 2)
        self.quantity = quantity
        self.description = description
        self.total = round(amount*quantity, 2)


class SalesPlan:
    __days = 0
    __productCost = 0
    __price = 0
    __costsPerSale = []
    __costsPerStep = []

    def __init__(self):
        pass

    def setProductCost(self, cost):
        self.__productCost = cost
        return self

    def getProductCost(self):
        return self.__productCost

    def setPrice(self, price=0):
        self.__price = price
        return self

    def setCostsPerSale(self, costsPerSale):
        if type(costsPerSale) != list:
            raise TypeError
        self.__costsPerSale = costsPerSale
        return self

    def addCostPerSale(self, costPerSale):
        if type(costPerSale) != Cost:
            raise TypeError
        self.__costsPerSale.append(costPerSale)

    def addCostPerStep(self, costPerStep):
        if type(costPerStep) != Cost:
            raise TypeError
        self.__costsPerStep.append(costPerStep)

    def setCostsPerStep(self, costsPerStep):
        if type(costsPerStep) != list:
            raise TypeError
        self.__costsPerStep = costsPerStep
        return self

    def getPrice(self):
        return self.__price

    def getCostsPerSale(self):
        return self.__costsPerSale

    def getCostsPerStep(self):
        return self.__costsPerStep

    def next(self):
        self.__days += 1


class Market:
    __successfulRate = 0
    __days = 0
    __salesRecords = []

    def __init__(self, successfulRate):
        self.__successfulRate = successfulRate

    def sell(self, price):
        sales = ((self.__days+1)*20, 200)[(self.__days+1)*20 > 200]
        if len(self.__salesRecords) is self.__days:
            self.__salesRecords.append([sales])
        else:
            self.__salesRecords[len(self.__salesRecords)-1].append(sales)
        return sales

    def getSuccessfulRate(self, price):
        return self.__successfulRate

    def getSalesRecords(self):
        if len(self.__salesRecords) is self.__days:
            self.__salesRecords.append([])
        return self.__salesRecords

    def getCombinedSalesRecords(self):
        if len(self.__salesRecords) is self.__days:
            self.__salesRecords.append([])
        c = []
        for a1 in self.__salesRecords:
            tmp = [0]
            for a2 in a1:
                tmp[0] += a2
            if len(a1) is 0:
                c.append([])
            else:
                c.append(tmp)
        return c

    def next(self):
        self.__days += 1


class Strategy:
    __accountant = None
    __storage = None
    __salesPlan = None
    __market = None
    __days = 0

    def __init__(self, firstDayPurchase):
        self.firstDayPurchase = firstDayPurchase

    def setSalesPlan(self, salesPlan):
        self.__salesPlan = salesPlan

    def setAccountant(self, accountant):
        self.__accountant = accountant
        return self

    def setStorage(self, storage):
        self.__storage = storage
        return self

    def setMarket(self, market):
        self.__market = market
        return self

    def makeStrategy(self):
        def fc(x, a, b, c=None, d=None, e=None, f=None, g=None, h=None):
            if not c:
                return a*x+b
            if not d:
                return a*x**2+b*x+c
            if not e:
                return a*x**3+b*x**2+c*x+d
            if not f:
                return a*x**4+b*x**3+c*x**2+d*x+e
            if not g:
                return a*x**5+b*x**4+c*x**3+d*x**2+e*x+f
            if not h:
                return a*x**6+b*x**5+c*x**4+d*x**3+e*x**2+f*x+g
            return a*x**7+b*x**6+c*x**5+d*x**4+e*x**3+f*x**2+g*x+h

        def f(l, length):
            for i in range(length - len(l)):
                l.append(None)
            return l
        futureStocks = self.__storage.getFutureStocks()
        stocks = self.__storage.getStocks()
        salesRecords = self.__market.getCombinedSalesRecords()
        if len(salesRecords[0]) is 0:
            self.__storage.addFutureStocks(
                self.firstDayPurchase, PURCHASE_PERIOD)
        elif NO_NUMPY or len(salesRecords) is 1:
            estimatedSales = salesRecords[0][0]
            estimatedSold = salesRecords[0][0] * PURCHASE_PERIOD
            estimatedStocks = stocks
            for i in range((len(futureStocks), PURCHASE_PERIOD)[len(futureStocks) > PURCHASE_PERIOD]):
                estimatedStocks += futureStocks[i]
            estimatedStocks -= estimatedSold
            lack = estimatedSales*STOCK_REDUNDANCY - estimatedStocks
            if lack > 0:
                self.__storage.addFutureStocks(lack, PURCHASE_PERIOD)
                self.__accountant.removeCash(
                    self.__salesPlan.getProductCost(), lack, '补货支出')
        else:
            x = np.array([x for x in range(0, self.__days+1)])
            y = np.array(list(map(lambda x: x[0], salesRecords)))
            order = (len(salesRecords)-1, 6)[len(salesRecords)-1 > 6]
            param = f(list(np.polyfit(x, y, order)), 7)
            estimatedSales = []
            for i in range(PURCHASE_PERIOD):
                estimatedSales.append(
                    fc(self.__days+i, param[0], param[1], param[2], param[3], param[4], param[5], param[6]))
            estimatedStocks = stocks
            for i in range(len(estimatedSales)):
                estimatedStocks += futureStocks[i]
                estimatedStocks -= estimatedSales[i]
            lack = estimatedSales[len(estimatedSales)-1]*STOCK_REDUNDANCY - \
                estimatedStocks
            if lack > 0:
                self.__storage.addFutureStocks(lack, PURCHASE_PERIOD)
                self.__accountant.removeCash(
                    self.__salesPlan.getProductCost(), lack, '补货支出')

    def next(self):
        self.__days += 1


class Storage:
    __stocks = 0
    __futureStocks = []
    __days = 0

    def __f(self, l, position, element):
        if position < len(l):
            l[position] += element
        else:
            for i in range(position-len(l)):
                l.append(0)
            l.append(element)

    def __init__(self):
        pass

    def exportStocks(self, quantity):
        quantity = int(quantity)
        if self.__stocks-quantity < 0:
            raise Exception(
                str('要求出库数量大于库存\n要求-'+str(quantity)+' 库存-'+str(self.__stocks)))
        self.__stocks -= quantity
        return self

    def importStocks(self, quantity):
        self.__stocks += int(quantity)
        return self

    def addFutureStocks(self, quantity, days):
        quantity = int(quantity)
        self.__f(self.__futureStocks, days-1, quantity)
        return self

    def getFutureStocks(self):
        return self.__futureStocks

    def getStocks(self):
        return self.__stocks

    def next(self):
        self.__days += 1
        if len(self.__futureStocks) > 0:
            self.__stocks += self.__futureStocks[0]
            self.__futureStocks = self.__futureStocks[1:]
        return


class Profiler:
    __data = []

    def __init__(self):
        pass

    def addStepData(self, data):
        self.__data.append(data)
        return self

    def profile(self, finalDay, accountant, err=None):
        for i in range(len(self.__data)):
            data = self.__data[i]
            print('第'+str(i+1)+'天')

            cpsl = 0
            cpst = 0
            for c in data.costsPerSale:
                cpsl += c.amount
            for c in data.costsPerStep:
                cpst += c.amount

            print('售出: ', str(data.sales), '库存: ', str(data.stocks),
                  '现金: ￥', str(data.cash), '总单个成本: ￥', str(cpsl), '本日总营运成本: ￥', str(cpst), '税前成本: ￥', str(cpsl*data.sales+cpst))
            print()
            print('单个成本')
            for c in data.costsPerSale:
                print(c.description+'    ￥'+str(c.amount))
            print()

            print('运营成本')
            for c in data.costsPerStep:
                print(c.description+'    ￥'+str(c.amount))
            print()

            transactions = accountant.getTransactions()[i]
            print('交易明细')
            for transaction in transactions:
                direction = ('收入', '支出')[transaction.direction is 'Withdrawal']
                print(transaction.description + '    ' + direction + '￥' + str(transaction.amount) +
                      ' * ' + str(transaction.quantity)+' = ￥' + str(transaction.total))
            print()

            rcab = []
            for dr in data.receivables:
                if len(dr) is 0:
                    rcab.append(0)
                else:
                    t = 0
                    for r in dr:
                        t += r['Transaction'].total
                    rcab.append(t)

            print('应收账款 -', rcab)
            print('未来库存 -', data.futureStocks)
            print('====')


class Accountant:
    __cash = 0
    __receivables = []
    __transactions = []
    __salesTax = 0
    __days = 0

    def __f(self, l, position, element):
        if position < len(l):
            l[position].append(element)
        else:
            for i in range(position-len(l)):
                l.append([])
            l.append([element])

    def __init__(self, cash):
        self.__cash = round(cash, 2)

    def setSalesTax(self, salesTax):
        self.__salesTax = salesTax
        return self

    def __addTransaction(self, direction, amount, quantity, description):
        if direction is not 'Deposit' and direction is not 'Withdrawal':
            raise TypeError
        transaction = Transaction(
            direction,
            amount,
            quantity,
            description)
        if len(self.__transactions) == self.__days:
            self.__transactions.append([transaction])
        else:
            self.__transactions[len(self.__transactions)-1].append(transaction)

    def addCash(self, amount, quantity, description, applyForSalesTax=False):
        amount = round(amount, 2)
        quantity = round(quantity)
        total = round(amount*quantity)
        self.__cash += total
        self.__addTransaction(
            'Deposit',
            amount,
            quantity,
            description)
        if applyForSalesTax and self.__salesTax > 0:
            self.removeCash(total*self.__salesTax, 1, '销售税')
        return self

    def removeCash(self, amount, quantity, description):
        amount = round(amount, 2)
        quantity = round(quantity)
        total = round(amount * quantity)
        if self.__cash - total < 0:
            raise Exception('现金不足')
        self.__cash -= round(total, 2)
        self.__addTransaction(
            'Withdrawal',
            amount,
            quantity,
            description)
        return self

    def getCash(self):
        return self.__cash

    def getTransactions(self):
        return self.__transactions

    def addReceivable(self, amount, quantity, description, days, applyForSalesTax=False):
        amount = round(amount, 2)
        quantity = round(quantity)
        self.__f(self.__receivables, days-1, {
                 'Transaction': Transaction(
                     'Deposit',
                     amount,
                     quantity,
                     description
                 ),
                 'ApplyForSalesTax': applyForSalesTax})
        return self

    def getReceivables(self):
        return self.__receivables

    def next(self):
        self.__days += 1
        if len(self.__receivables) > 0:
            for r in self.__receivables[0]:
                tsn = r['Transaction']
                self.addCash(tsn.amount,
                             tsn.quantity,
                             tsn.description,
                             r['ApplyForSalesTax'])
            self.__receivables = self.__receivables[1:]


def executor(args, accountant, salesPlan, strategy, market, storage, profiler):
    day = args['Day']
    strategy.setAccountant(accountant)
    strategy.setStorage(storage)
    strategy.setSalesPlan(salesPlan)
    d = 0
    try:
        while d < day:
            price = salesPlan.getPrice()
            sales = market.sell(price)
            costsPerSale = salesPlan.getCostsPerSale()
            costsPerStep = salesPlan.getCostsPerStep()
            successfulRate = market.getSuccessfulRate(price)
            succ = round(sales*successfulRate)
            fail = sales - succ

            for cost in costsPerSale:
                accountant.removeCash(cost.amount, sales, cost.description)
            for cost in costsPerStep:
                accountant.removeCash(cost.amount, 1, cost.description)

            accountant.addReceivable(price, sales, '收款', PAYBACK_PERIOD)

            storage.exportStocks(sales)
            storage.addFutureStocks(fail, SHIPBACK_PERIOD)

            stocks = storage.getStocks()
            receivables = accountant.getReceivables()

            strategy.makeStrategy()

            salesPlan.next()
            strategy.next()
            storage.next()
            accountant.next()
            market.next()

            futureStocks = storage.getFutureStocks()
            cash = accountant.getCash()
            transaction = accountant.getTransactions()

            result = DayResult(
                price,
                sales,
                successfulRate,
                succ,
                fail,
                costsPerSale,
                costsPerStep,
                stocks,
                futureStocks,
                cash,
                transaction,
                receivables
            )

            cpsl = 0
            for a in costsPerSale:
                cpsl += a.amount

            cpst = 0
            for a in costsPerStep:
                cpst += a.amount

            profiler.addStepData(result)
            d += 1
        profiler.profile(d, accountant)
    except Exception as err:
        raise err
        #profiler.profile(d, err)


acc = Accountant(1000000)
acc.setSalesTax(0.035)

sto = Storage()
sto.importStocks(300)

n = sto.next
e = sto.exportStocks
i = sto.importStocks
a = sto.addFutureStocks
g = sto.getStocks
gf = sto.getFutureStocks

m = Market(0.85)

sp = SalesPlan()
sp.setProductCost(25)
sp.setPrice(100)
sp.addCostPerSale(Cost('广告费', 25))
sp.addCostPerSale(Cost('运费', 4))
sp.addCostPerStep(Cost('运营成本', 200))

st = Strategy(200)
st.setSalesPlan(sp)
st.setMarket(m)
st.setAccountant(acc)
st.setStorage(sto)

p = Profiler()

executor({'Day': 30}, acc, sp, st, m, sto, p)
